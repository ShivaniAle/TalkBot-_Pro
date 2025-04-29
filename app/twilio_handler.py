# app/twilio_handler.py

from fastapi import APIRouter, Request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import requests
import os
import logging
import time
from dotenv import load_dotenv
import base64
from app.config import settings
from typing import Dict, Any, Optional, Callable, Awaitable
from app.utils import mask_sensitive_data
from app.openai_handler import OpenAIClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Twilio client with uppercase settings
client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

router = APIRouter()

class TwilioHandler:
    def __init__(self):
        """Initialize Twilio handler"""
        try:
            if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
                raise ValueError("Twilio credentials not set in environment variables")
            
            self.openai_client = OpenAIClient()
            logger.info("Twilio handler initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Twilio handler: {str(e)}")
            raise

    async def handle_voice(self, request: Request) -> Response:
        """Handle incoming voice call with natural conversation settings"""
        try:
            response = VoiceResponse()
            
            # Set up natural conversation settings
            gather = Gather(
                input="speech dtmf",
                action="/twilio/speech",
                method="POST",
                timeout=2,  # Shorter timeout for more natural flow
                speechTimeout="auto",
                language="en-US",
                speechModel="phone_call",
                enhanced="true",
                bargeIn="true",
                actionOnEmptyResult="true",
                finishOnKey="*",
                partialResultCallback="/twilio/speech",
                partialResultCallbackMethod="POST",
                hints="interrupt,stop,wait",
                speechRecognitionSensitivity="high",
                speechRecognitionConfidence="high",
                speechRecognitionTimeout="auto",
                speechRecognitionLanguage="en-US",
                speechRecognitionModel="phone_call",
                speechRecognitionProfanityFilter="false",
                speechRecognitionPartialResults="true",
                speechRecognitionHints="interrupt,stop,wait"
            )
            
            # Add natural greeting with pauses
            gather.say(
                "Hey there! <break time='0.5s'/> It's great to hear from you. <break time='0.3s'/> What's on your mind?",
                voice="Polly.Amy",
                language="en-GB"
            )
            
            response.append(gather)
            return Response(str(response), mimetype="application/xml")
            
        except Exception as e:
            logger.error(f"Error in handle_voice: {str(e)}")
            response = VoiceResponse()
            response.say("I'm having some trouble. Could you please try again?")
            return Response(str(response), mimetype="application/xml")

    async def handle_speech(self, request: Request) -> Response:
        """Handle speech recognition results with natural conversation flow"""
        try:
            form_data = await request.form()
            speech_result = form_data.get("SpeechResult", "").strip()
            confidence = float(form_data.get("Confidence", 0))
            interrupted = form_data.get("Interrupted", "false").lower() == "true"
            
            logger.info(f"Speech result: {speech_result}, Confidence: {confidence}, Interrupted: {interrupted}")
            
            # Create response object
            response = VoiceResponse()
            
            # If speech was interrupted, handle it naturally
            if interrupted:
                logger.info("Handling interrupted speech")
                # Create a stop response to immediately halt current speech
                stop_response = VoiceResponse()
                stop_response.say("", voice="Polly.Amy", language="en-GB")  # Empty say command to stop current speech
                
                # Process the interruption immediately
                try:
                    # Get AI response for the interruption
                    ai_response = await self.openai_client.get_response(speech_result)
                    
                    if not ai_response:
                        raise Exception("Empty response from AI")
                    
                    # Configure voice response for natural conversation
                    gather = Gather(
                        input="speech dtmf",
                        action="/twilio/speech",
                        method="POST",
                        timeout=1,  # Very short timeout for immediate response
                        speechTimeout="auto",
                        language="en-US",
                        speechModel="phone_call",
                        enhanced="true",
                        bargeIn="true",
                        actionOnEmptyResult="true",
                        finishOnKey="*",
                        partialResultCallback="/twilio/speech",
                        partialResultCallbackMethod="POST",
                        hints="interrupt,stop,wait",
                        speechRecognitionSensitivity="high",
                        speechRecognitionConfidence="high",
                        speechRecognitionTimeout="auto",
                        speechRecognitionLanguage="en-US",
                        speechRecognitionModel="phone_call",
                        speechRecognitionProfanityFilter="false",
                        speechRecognitionPartialResults="true",
                        speechRecognitionHints="interrupt,stop,wait"
                    )
                    
                    # Add AI response with natural pauses
                    gather.say(ai_response, voice="Polly.Amy", language="en-GB")
                    stop_response.append(gather)
                    
                    return Response(str(stop_response), mimetype="application/xml")
                    
                except Exception as e:
                    logger.error(f"Error handling interruption: {str(e)}")
                    stop_response.say("I'm having trouble understanding. Could you please repeat that?")
                    gather = Gather(
                        input="speech dtmf",
                        action="/twilio/speech",
                        method="POST",
                        timeout=1,
                        speechTimeout="auto",
                        language="en-US",
                        speechModel="phone_call",
                        enhanced="true",
                        bargeIn="true",
                        actionOnEmptyResult="true",
                        finishOnKey="*",
                        partialResultCallback="/twilio/speech",
                        partialResultCallbackMethod="POST",
                        hints="interrupt,stop,wait",
                        speechRecognitionSensitivity="high",
                        speechRecognitionConfidence="high",
                        speechRecognitionTimeout="auto",
                        speechRecognitionLanguage="en-US",
                        speechRecognitionModel="phone_call",
                        speechRecognitionProfanityFilter="false",
                        speechRecognitionPartialResults="true",
                        speechRecognitionHints="interrupt,stop,wait"
                    )
                    stop_response.append(gather)
                    return Response(str(stop_response), mimetype="application/xml")
            
            # Process speech if confidence is adequate
            if confidence >= 0.1:
                try:
                    # Get AI response with conversation context
                    ai_response = await self.openai_client.get_response(speech_result)
                    
                    if not ai_response:
                        raise Exception("Empty response from AI")
                    
                    # Configure voice response for natural conversation
                    gather = Gather(
                        input="speech dtmf",
                        action="/twilio/speech",
                        method="POST",
                        timeout=1,
                        speechTimeout="auto",
                        language="en-US",
                        speechModel="phone_call",
                        enhanced="true",
                        bargeIn="true",
                        actionOnEmptyResult="true",
                        finishOnKey="*",
                        partialResultCallback="/twilio/speech",
                        partialResultCallbackMethod="POST",
                        hints="interrupt,stop,wait",
                        speechRecognitionSensitivity="high",
                        speechRecognitionConfidence="high",
                        speechRecognitionTimeout="auto",
                        speechRecognitionLanguage="en-US",
                        speechRecognitionModel="phone_call",
                        speechRecognitionProfanityFilter="false",
                        speechRecognitionPartialResults="true",
                        speechRecognitionHints="interrupt,stop,wait"
                    )
                    
                    # Add AI response with natural pauses
                    gather.say(ai_response, voice="Polly.Amy", language="en-GB")
                    response.append(gather)
                    
                except Exception as e:
                    logger.error(f"Error getting AI response: {str(e)}")
                    response.say("I'm having trouble understanding. Could you please repeat that?")
                    gather = Gather(
                        input="speech dtmf",
                        action="/twilio/speech",
                        method="POST",
                        timeout=1,
                        speechTimeout="auto",
                        language="en-US",
                        speechModel="phone_call",
                        enhanced="true",
                        bargeIn="true",
                        actionOnEmptyResult="true",
                        finishOnKey="*",
                        partialResultCallback="/twilio/speech",
                        partialResultCallbackMethod="POST",
                        hints="interrupt,stop,wait",
                        speechRecognitionSensitivity="high",
                        speechRecognitionConfidence="high",
                        speechRecognitionTimeout="auto",
                        speechRecognitionLanguage="en-US",
                        speechRecognitionModel="phone_call",
                        speechRecognitionProfanityFilter="false",
                        speechRecognitionPartialResults="true",
                        speechRecognitionHints="interrupt,stop,wait"
                    )
                    response.append(gather)
            else:
                # If confidence is low, ask for repetition more naturally
                response.say("I didn't quite catch that. Could you say that again?")
                gather = Gather(
                    input="speech dtmf",
                    action="/twilio/speech",
                    method="POST",
                    timeout=1,
                    speechTimeout="auto",
                    language="en-US",
                    speechModel="phone_call",
                    enhanced="true",
                    bargeIn="true",
                    actionOnEmptyResult="true",
                    finishOnKey="*",
                    partialResultCallback="/twilio/speech",
                    partialResultCallbackMethod="POST",
                    hints="interrupt,stop,wait",
                    speechRecognitionSensitivity="high",
                    speechRecognitionConfidence="high",
                    speechRecognitionTimeout="auto",
                    speechRecognitionLanguage="en-US",
                    speechRecognitionModel="phone_call",
                    speechRecognitionProfanityFilter="false",
                    speechRecognitionPartialResults="true",
                    speechRecognitionHints="interrupt,stop,wait"
                )
                response.append(gather)
            
            return Response(str(response), mimetype="application/xml")
            
        except Exception as e:
            logger.error(f"Error in handle_speech: {str(e)}")
            response = VoiceResponse()
            response.say("I'm having some trouble. Could you please try again?")
            gather = Gather(
                input="speech dtmf",
                action="/twilio/speech",
                method="POST",
                timeout=1,
                speechTimeout="auto",
                language="en-US",
                speechModel="phone_call",
                enhanced="true",
                bargeIn="true",
                actionOnEmptyResult="true",
                finishOnKey="*",
                partialResultCallback="/twilio/speech",
                partialResultCallbackMethod="POST",
                hints="interrupt,stop,wait",
                speechRecognitionSensitivity="high",
                speechRecognitionConfidence="high",
                speechRecognitionTimeout="auto",
                speechRecognitionLanguage="en-US",
                speechRecognitionModel="phone_call",
                speechRecognitionProfanityFilter="false",
                speechRecognitionPartialResults="true",
                speechRecognitionHints="interrupt,stop,wait"
            )
            response.append(gather)
            return Response(str(response), mimetype="application/xml")

# Initialize Twilio handler instance
twilio_handler = TwilioHandler()

@router.post("/twilio/voice")
async def handle_voice(request: Request):
    """Handle initial voice call"""
    try:
        logger.info("Received voice call")
        
        # Get form data
        form_data = await request.form()
        if not form_data:
            logger.error("No form data received")
            raise ValueError("No form data received")
            
        # Process voice call using TwilioHandler
        response = await twilio_handler.handle_voice(request)
        return response
            
    except Exception as e:
        logger.error(f"Error in voice endpoint: {str(e)}", exc_info=True)
        response = VoiceResponse()
        response.say(
            "I'm sorry, there was an error. Please try again.",
            voice="alice",
            language="en-US"
        )
        return Response(content=str(response), media_type="application/xml")

@router.post("/twilio/speech")
async def handle_speech(request: Request):
    """Handle speech input from user"""
    try:
        logger.info("Received speech input")
        
        # Get form data
        form_data = await request.form()
        if not form_data:
            logger.error("No form data received")
            raise ValueError("No form data received")
            
        # Process speech using TwilioHandler
        response = await twilio_handler.handle_speech(request)
        return response
            
    except ValueError as e:
        logger.error(f"Invalid request data: {str(e)}", exc_info=True)
        response = VoiceResponse()
        response.say(
            "I'm sorry, I didn't receive your message properly. Please try again.",
            voice="alice",
            language="en-US"
        )
        gather = Gather(
            input='speech',
            action='/twilio/speech',
            method='POST',
            language='en-US',
            speechTimeout='auto',
            enhanced='true',
            speechModel='phone_call',
            timeout=3
        )
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Unexpected error in speech endpoint: {str(e)}", exc_info=True)
        response = VoiceResponse()
        response.say(
            "I'm sorry, there was an unexpected error. Please try again.",
            voice="alice",
            language="en-US"
        )
        gather = Gather(
            input='speech',
            action='/twilio/speech',
            method='POST',
            language='en-US',
            speechTimeout='auto',
            enhanced='true',
            speechModel='phone_call',
            timeout=3
        )
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")
