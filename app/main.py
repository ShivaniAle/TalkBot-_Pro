import os
import logging
from fastapi import FastAPI, Request, Response, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.twilio_handler import TwilioHandler
from app.openai_handler import OpenAIClient
from app.gcp_handler import GCPClient
from app.audio_processor import AudioProcessor
from typing import Dict, Optional
import uuid
import asyncio
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from app.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get port from environment variable
PORT = int(os.getenv("PORT", "9000"))
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

# Initialize service clients silently
try:
    # Redirect stdout temporarily to suppress client initialization messages
    import sys
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    twilio_handler = TwilioHandler()
    openai_client = OpenAIClient()
    gcp_client = GCPClient()
    audio_processor = AudioProcessor()
    
    # Restore stdout
    sys.stdout = old_stdout
except Exception as e:
    logger.error(f"Failed to initialize service clients: {str(e)}")
    raise

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

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
    """Handle incoming voice calls with natural conversation flow"""
    try:
        logger.info("Received voice call")
        response = await twilio_handler.handle_voice(request)
        return Response(str(response), media_type="application/xml")
    except Exception as e:
        logger.error(f"Error handling voice call: {str(e)}", exc_info=True)
        response = VoiceResponse()
        response.say("I'm having some trouble. Could you please try again?")
        return Response(str(response), media_type="application/xml")

@app.post("/twilio/speech")
async def handle_speech(request: Request):
    """Handle speech input with natural conversation flow"""
    try:
        logger.info("Received speech input")
        response = await twilio_handler.handle_speech(request)
        return Response(str(response), media_type="application/xml")
    except Exception as e:
        logger.error(f"Error handling speech input: {str(e)}", exc_info=True)
        response = VoiceResponse()
        response.say("I'm having some trouble. Could you please try again?")
        return Response(str(response), media_type="application/xml")

@app.post("/twilio/continue")
async def handle_continue(request: Request):
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        speech_result = form_data.get("SpeechResult", "").lower()
        
        response = VoiceResponse()
        
        if "yes" in speech_result or "yeah" in speech_result or "sure" in speech_result:
            response.say("Great! What would you like to talk about?", voice="alice", bargeIn="true")
            
            gather = Gather(
                input="speech",
                action="/twilio/speech",
                method="POST",
                timeout=3,
                speechTimeout="auto",
                language="en-US",
                enhanced="true",
                profanityFilter="false",
                bargeIn="true"
            )
            response.append(gather)
            
        else:
            if speech_result:
                conversation = get_conversation(call_sid)
                if conversation:
                    conversation["messages"].append({
                        "role": "user",
                        "content": speech_result
                    })
                    
                    try:
                        # Get response from OpenAI without conversation_history parameter
                        ai_response = await openai_client.get_response(speech_result)
                        
                        conversation["messages"].append({
                            "role": "assistant",
                            "content": ai_response
                        })
                        
                        response.say(ai_response, voice="alice", bargeIn="true")
                        
                        gather = Gather(
                            input="speech",
                            action="/twilio/speech",
                            method="POST",
                            timeout=3,
                            speechTimeout="auto",
                            language="en-US",
                            enhanced="true",
                            profanityFilter="false",
                            bargeIn="true"
                        )
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
    """Health check endpoint"""
    return {"status": "healthy"}

@app.websocket("/ws/audio/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Handle WebSocket connections for real-time audio streaming"""
    try:
        await websocket.accept()
        active_connections[client_id] = websocket
        logger.info(f"WebSocket connection established for client {client_id}")
        
        # Start audio streaming
        audio_stream = audio_processor.start_streaming()
        
        try:
            while True:
                # Receive audio data from client
                audio_data = await websocket.receive_bytes()
                
                # Process audio through MCP
                processed_chunk = await audio_processor._process_audio_chunk(audio_data)
                
                # Get streaming response from OpenAI
                async for response_chunk in openai_client.get_streaming_response(str(audio_data)):
                    # Send response chunk back to client
                    await websocket.send_text(response_chunk)
                
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {str(e)}")
            raise
            
    finally:
        # Clean up connection
        if client_id in active_connections:
            del active_connections[client_id]
        audio_processor.stop_streaming()
        await websocket.close()

@app.post("/voice")
async def voice_endpoint(request: Request):
    """Handle incoming voice calls"""
    try:
        logger.info("Received voice request")
        
        # Handle voice request through Twilio
        response = await twilio_handler.handle_voice(request)
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error in voice endpoint: {str(e)}", exc_info=True)
        response = VoiceResponse()
        response.say("I'm sorry, I'm having trouble processing your request. Please try again later.")
        return Response(content=str(response), media_type="application/xml")

@app.post("/speech")
async def speech_endpoint(request: Request):
    """Handle speech recognition results"""
    try:
        logger.info("Received speech request")
        
        # Process speech through Twilio handler
        response = await twilio_handler.handle_speech(request)
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error in speech endpoint: {str(e)}", exc_info=True)
        response = VoiceResponse()
        response.say("I'm sorry, I'm having trouble processing your request. Please try again later.")
        return Response(content=str(response), media_type="application/xml")

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
        # Run uvicorn with minimal output
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=PORT,
            reload=True,
            log_level="critical",
            access_log=False  # Disable access logs
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
    finally:
        logger.info("Server shutdown complete")