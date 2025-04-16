import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse
from app.twilio_handler import TwilioHandler
from app.openai_handler import OpenAIClient
from app.gcp_handler import GCPClient

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get port from environment variable
PORT = int(os.getenv("PORT", "8080"))
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

# Initialize service clients
try:
    logger.info("Initializing Twilio client...")
    twilio_handler = TwilioHandler()
    
    logger.info("Initializing OpenAI client...")
    openai_client = OpenAIClient()
    
    logger.info("Initializing GCP client...")
    gcp_client = GCPClient()
    
    logger.info("All service clients initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize service clients: {str(e)}")
    raise

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Voice AI Agent is running"}

@app.post("/voice")
async def handle_voice(request: Request):
    try:
        logger.info("Received voice request")
        response = VoiceResponse()
        response.say("Hello! I'm your AI assistant. Please speak after the beep.")
        response.record(
            action="/speech",
            method="POST",
            maxLength="30",
            playBeep=True,
            transcribe=True
        )
        return str(response)
    except Exception as e:
        logger.error(f"Error in voice endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/speech")
async def handle_speech(request: Request):
    try:
        logger.info("Received speech request")
        form_data = await request.form()
        transcription = form_data.get("TranscriptionText", "")
        
        if not transcription:
            logger.warning("No transcription text received")
            return {"message": "No speech detected"}
        
        logger.info(f"Processing transcription: {transcription}")
        
        # Get AI response
        ai_response = await openai_client.get_response(transcription)
        
        # Store conversation in GCP
        await gcp_client.store_conversation(transcription, ai_response)
        
        response = VoiceResponse()
        response.say(ai_response)
        response.hangup()
        
        return str(response)
    except Exception as e:
        logger.error(f"Error in speech endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    try:
        logger.info("Performing health check...")
        # Check if all required services are initialized
        services = {
            "twilio": twilio_handler is not None,
            "openai": openai_client is not None,
            "gcp": gcp_client is not None
        }
        
        # If any service is not initialized, return unhealthy
        if not all(services.values()):
            logger.error(f"Health check failed: Services not initialized: {services}")
            return {"status": "unhealthy", "services": services}
            
        logger.info("Health check passed successfully")
        return {
            "status": "healthy",
            "services": services,
            "port": PORT
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)