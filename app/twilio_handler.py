# app/twilio_handler.py

from fastapi import APIRouter, Request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import requests
import os
import logging
import time
from dotenv import load_dotenv
import base64
from app.config import settings
from app.openai_handler import OpenAIClient
from app.gcp_handler import GCPClient
from typing import Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Twilio client
twilio_client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

router = APIRouter()

class TwilioHandler:
    def __init__(self):
        """Initialize the Twilio handler"""
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        logger.info("Twilio handler initialized")

    async def handle_voice(self, form_data: Dict[str, Any]) -> str:
        """Handle incoming voice calls"""
        try:
            logger.info("Processing voice call")
            response = VoiceResponse()
            
            # Add a greeting
            response.say("Hello! I'm your AI assistant. How can I help you today?")
            
            # Add a gather element to collect speech
            gather = Gather(
                input='speech',
                action='/speech',
                method='POST',
                language='en-US',
                speechTimeout='auto'
            )
            gather.say("Please speak your question or request.")
            response.append(gather)
            
            # If no speech is detected, say goodbye
            response.say("I didn't catch that. Goodbye!")
            
            return str(response)
        except Exception as e:
            logger.error(f"Error handling voice call: {str(e)}", exc_info=True)
            raise

    async def handle_speech(self, form_data: Dict[str, Any], openai_client: Any) -> str:
        """Handle speech results from Twilio"""
        try:
            logger.info("Processing speech result")
            response = VoiceResponse()
            
            # Get the speech result
            speech_result = form_data.get('SpeechResult', '')
            logger.info(f"Received speech: {speech_result}")
            
            if not speech_result:
                logger.warning("No speech result received")
                response.say("I didn't catch that. Please try again.")
                return str(response)
            
            # Get response from OpenAI
            try:
                logger.info("Sending request to OpenAI")
                ai_response = await openai_client.get_response(speech_result)
                logger.info(f"OpenAI response: {ai_response}")
                
                if not ai_response:
                    logger.error("Empty response received from OpenAI")
                    response.say("I'm sorry, I didn't get a response. Please try again.")
                else:
                    response.say(ai_response)
            except Exception as e:
                logger.error(f"Error getting OpenAI response: {str(e)}", exc_info=True)
                response.say("I'm sorry, I encountered an error processing your request. Please try again.")
            
            # Add another gather for follow-up
            gather = Gather(
                input='speech',
                action='/speech',
                method='POST',
                language='en-US',
                speechTimeout='auto'
            )
            gather.say("Is there anything else I can help you with?")
            response.append(gather)
            
            # If no speech is detected, say goodbye
            response.say("I didn't catch that. Goodbye!")
            
            return str(response)
        except Exception as e:
            logger.error(f"Error handling speech: {str(e)}", exc_info=True)
            raise

@router.post("/twilio/voice")
async def handle_voice(request: Request):
    """Handle initial voice call"""
    try:
        logger.info("Received voice call")
        response = VoiceResponse()
        
        # Create a Gather verb to collect user speech
        gather = Gather(
            input='speech',
            action='/twilio/handle-speech',
            method='POST',
            language='en-US',
            speechTimeout='auto',
            enhanced='true'  # Use enhanced speech recognition
        )
        
        # Add initial greeting
        gather.say("Hello! I'm your AI assistant. How can I help you today?")
        response.append(gather)
        
        # If no input received, add a fallback message
        response.say("I didn't catch that. Please try again.")
        
        logger.info("Sending initial voice response")
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error in handle_voice: {str(e)}", exc_info=True)
        response = VoiceResponse()
        response.say("Sorry, there was an error processing your call. Please try again later.")
        return Response(content=str(response), media_type="application/xml")

@router.post("/twilio/handle-speech")
async def handle_speech(request: Request):
    """Handle speech input from user"""
    try:
        form = await request.form()
        logger.info(f"Received form data: {form}")
        
        speech_result = form.get("SpeechResult", "")
        logger.info(f"Received speech: {speech_result}")
        
        if not speech_result:
            logger.warning("No speech result received")
            response = VoiceResponse()
            response.say("I didn't catch that. Could you please repeat?")
            response.redirect('/twilio/voice')
            return Response(content=str(response), media_type="application/xml")
        
        # Initialize clients
        try:
            openai_client = OpenAIClient()
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}", exc_info=True)
            raise
        
        try:
            gcp_client = GCPClient()
            logger.info("GCP client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing GCP client: {str(e)}", exc_info=True)
            raise
        
        # Get response from OpenAI
        try:
            ai_response = await openai_client.get_response(speech_result)
            logger.info(f"AI Response: {ai_response}")
        except Exception as e:
            logger.error(f"Error getting OpenAI response: {str(e)}", exc_info=True)
            raise
        
        # Create TwiML response
        response = VoiceResponse()
        
        # Convert AI response to speech and store in GCP
        try:
            audio_file = await gcp_client.text_to_speech(ai_response)
            if audio_file.url:  # If we have a URL, use it
                logger.info(f"Using GCP TTS with URL: {audio_file.url}")
                response.play(audio_file.url)
            else:  # Fallback to Twilio's TTS
                logger.info("Using Twilio TTS fallback")
                response.say(ai_response)
        except Exception as e:
            logger.error(f"Error in text-to-speech: {str(e)}", exc_info=True)
            # Fallback to basic TTS
            response.say(ai_response)
        
        # Add option to continue conversation
        gather = Gather(
            input='speech',
            action='/twilio/handle-speech',
            method='POST',
            language='en-US',
            speechTimeout='auto'
        )
        gather.say("Is there anything else I can help you with?")
        response.append(gather)
        
        logger.info("Sending speech response")
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error in handle_speech: {str(e)}", exc_info=True)
        response = VoiceResponse()
        response.say("Sorry, there was an error processing your request. Please try again.")
        return Response(content=str(response), media_type="application/xml")
