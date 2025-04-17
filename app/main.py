import os
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.twilio_handler import TwilioHandler
from app.openai_handler import OpenAIClient
from app.gcp_handler import GCPClient
from typing import Dict, Optional
import uuid

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get port from environment variable
PORT = int(os.getenv("PORT", "8000"))
logger.info(f"Starting application on port {PORT}")

# Initialize FastAPI app
app = FastAPI(title="Voice AI Agent")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active conversations
active_conversations: Dict[str, dict] = {}

# Initialize service clients
try:
    logger.info("Initializing service clients...")
    twilio_handler = TwilioHandler()
    openai_client = OpenAIClient()
    gcp_client = GCPClient()
except Exception as e:
    logger.error(f"Failed to initialize service clients: {str(e)}")
    raise

def create_conversation(call_sid: str) -> dict:
    """Create a new conversation entry"""
    conversation = {
        "call_sid": call_sid,
        "messages": []
    }
    active_conversations[call_sid] = conversation
    return conversation

def get_conversation(call_sid: str) -> Optional[dict]:
    """Get an existing conversation"""
    return active_conversations.get(call_sid)

@app.get("/")
async def root():
    return {"message": "Voice AI Agent is running"}

@app.post("/twilio/voice")
async def handle_voice(request: Request):
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid", str(uuid.uuid4()))
        logger.info(f"New call received: {call_sid}")
        
        conversation = get_conversation(call_sid) or create_conversation(call_sid)
        
        response = VoiceResponse()
        response.say("Hello! I'm your AI assistant. What would you like to talk about?", voice="alice")
        response.pause(length=2)
        
        gather = Gather(
            input="speech",
            action="/twilio/speech",
            method="POST",
            timeout=10,
            speechTimeout="auto",
            language="en-US",
            enhanced="true",
            profanityFilter="false"
        )
        response.append(gather)
        
        response.say("I'm sorry, I couldn't hear you. Please try again.", voice="alice")
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error in voice endpoint: {str(e)}")
        response = VoiceResponse()
        response.say("I'm sorry, there was an error. Please try again later.", voice="alice")
        return Response(content=str(response), media_type="application/xml")

@app.post("/twilio/speech")
async def handle_speech(request: Request):
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        speech_result = form_data.get("SpeechResult", "")
        
        logger.info(f"Speech received: {speech_result[:50]}...")
        
        if not call_sid or not speech_result:
            response = VoiceResponse()
            response.say("I'm sorry, I couldn't hear what you said. Please try again.", voice="alice")
            return Response(content=str(response), media_type="application/xml")
        
        conversation = get_conversation(call_sid) or create_conversation(call_sid)
        conversation["messages"].append({"role": "user", "content": speech_result})
        
        try:
            conversation_history = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation["messages"][-5:]
            ])
            
            ai_response = await openai_client.get_response(
                speech_result,
                conversation_history=conversation_history
            )
            
            conversation["messages"].append({
                "role": "assistant",
                "content": ai_response
            })
            
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            response = VoiceResponse()
            response.say("I'm sorry, I'm having trouble processing your request. Please try again later.", voice="alice")
            return Response(content=str(response), media_type="application/xml")
        
        response = VoiceResponse()
        response.pause(length=3)
        response.say(ai_response, voice="alice")
        response.pause(length=3)
        
        gather = Gather(
            input="speech",
            action="/twilio/continue",
            method="POST",
            timeout=10,
            speechTimeout="auto"
        )
        gather.say("Would you like to continue our conversation? Please say yes or no.", voice="alice")
        response.append(gather)
        
        response.say("Thank you for calling. Goodbye!", voice="alice")
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error in speech endpoint: {str(e)}")
        response = VoiceResponse()
        response.say("I'm sorry, there was an error processing your request. Please try again later.", voice="alice")
        return Response(content=str(response), media_type="application/xml")

@app.post("/twilio/continue")
async def handle_continue(request: Request):
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        speech_result = form_data.get("SpeechResult", "").lower()
        
        logger.info(f"Continue request: {speech_result[:50]}...")
        
        response = VoiceResponse()
        response.pause(length=3)
        
        if "yes" in speech_result or "yeah" in speech_result or "sure" in speech_result:
            response.say("Great! What would you like to talk about?", voice="alice")
            response.pause(length=3)
            
            gather = Gather(
                input="speech",
                action="/twilio/speech",
                method="POST",
                timeout=10,
                speechTimeout="auto",
                language="en-US",
                enhanced="true",
                profanityFilter="false"
            )
            response.append(gather)
            
            response.say("I'm sorry, I couldn't hear you. Please try again.", voice="alice")
            
        else:
            if speech_result:
                conversation = get_conversation(call_sid)
                if conversation:
                    conversation["messages"].append({
                        "role": "user",
                        "content": speech_result
                    })
                    
                    try:
                        conversation_history = "\n".join([
                            f"{msg['role']}: {msg['content']}"
                            for msg in conversation["messages"][-5:]
                        ])
                        
                        ai_response = await openai_client.get_response(
                            speech_result,
                            conversation_history=conversation_history
                        )
                        
                        conversation["messages"].append({
                            "role": "assistant",
                            "content": ai_response
                        })
                        
                        response.pause(length=3)
                        response.say(ai_response, voice="alice")
                        response.pause(length=3)
                        
                        gather = Gather(
                            input="speech",
                            action="/twilio/continue",
                            method="POST",
                            timeout=10,
                            speechTimeout="auto"
                        )
                        gather.say("Would you like to continue our conversation? Please say yes or no.", voice="alice")
                        response.append(gather)
                        
                    except Exception as e:
                        logger.error(f"Error getting AI response: {str(e)}")
                        response.say("I'm sorry, I'm having trouble processing your request. Please try again later.", voice="alice")
            else:
                response.say("Thank you for the conversation. Goodbye!", voice="alice")
                if call_sid in active_conversations:
                    del active_conversations[call_sid]
        
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error in continue endpoint: {str(e)}")
        response = VoiceResponse()
        response.say("I'm sorry, there was an error. Goodbye!", voice="alice")
        return Response(content=str(response), media_type="application/xml")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    import signal
    import sys
    
    def signal_handler(sig, frame):
        logger.info("Shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info(f"Starting server on port {PORT}")
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=PORT,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
    finally:
        logger.info("Server shutdown complete")