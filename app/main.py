from fastapi import FastAPI, Request, HTTPException
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.twilio_handler import router as twilio_router, TwilioHandler
from app.openai_handler import OpenAIClient
from app.gcp_handler import GCPClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice AI Agent")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the Twilio router
app.include_router(twilio_router)

# Initialize clients
twilio_handler = TwilioHandler()
openai_client = OpenAIClient()
gcp_client = GCPClient()

@app.post("/voice")
async def handle_voice(request: Request):
    """Handle incoming voice calls"""
    try:
        logger.info("Received voice call request")
        form_data = await request.form()
        return await twilio_handler.handle_voice(form_data)
    except Exception as e:
        logger.error(f"Error handling voice call: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/speech")
async def handle_speech(request: Request):
    """Handle speech results from Twilio"""
    try:
        logger.info("Received speech result")
        form_data = await request.form()
        return await twilio_handler.handle_speech(form_data, openai_client)
    except Exception as e:
        logger.error(f"Error handling speech: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Voice AI Agent API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting voice agent server")
    uvicorn.run(app, host="0.0.0.0", port=8000)