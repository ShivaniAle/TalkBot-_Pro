from twilio.twiml.voice_response import VoiceResponse, Gather
from app.openai_handler import OpenAIClient
from app.config import settings
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

class TwilioHandler:
    def __init__(self):
        """Initialize the Twilio handler"""
        try:
            logger.info("Initializing Twilio handler...")
            
            # Validate required settings
            if not settings.TWILIO_ACCOUNT_SID:
                raise ValueError("TWILIO_ACCOUNT_SID is not set")
            if not settings.TWILIO_AUTH_TOKEN:
                raise ValueError("TWILIO_AUTH_TOKEN is not set")
            if not settings.TWILIO_PHONE_NUMBER:
                raise ValueError("TWILIO_PHONE_NUMBER is not set")
            
            # Initialize OpenAI client
            self.openai_client = OpenAIClient()
            
            # Store active conversations
            self.active_conversations = {}
            
            logger.info("Twilio handler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twilio handler: {str(e)}", exc_info=True)
            raise

    def get_conversation_id(self, request: Request) -> str:
        """Get or create conversation ID from request"""
        form_data = request.form()
        call_sid = form_data.get("CallSid", "default")
        return call_sid

    async def handle_voice(self, request: Request) -> str:
        """Handle incoming voice call"""
        try:
            response = VoiceResponse()
            
            # Get conversation ID
            conversation_id = self.get_conversation_id(request)
            
            # Add a warm, conversational greeting
            response.say("Hi there! It's great to hear from you. What would you like to chat about today?", voice="alice", bargeIn="true")
            
            # Set up speech recognition with enhanced settings
            gather = Gather(
                input="speech",
                action="/twilio/speech",
                method="POST",
                timeout=5,
                speechTimeout="auto",
                language="en-US",
                enhanced="true",
                profanityFilter="false",
                bargeIn="true",
                speechModel="phone_call"
            )
            
            response.append(gather)
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Error handling voice call: {str(e)}", exc_info=True)
            response = VoiceResponse()
            response.say("I'm sorry, I'm having trouble understanding. Please try again.")
            return str(response)

    async def handle_speech(self, request: Request) -> str:
        """Handle speech recognition results"""
        try:
            # Get speech result from request
            form_data = await request.form()
            speech_result = form_data.get("SpeechResult", "")
            confidence = float(form_data.get("Confidence", 0))
            conversation_id = form_data.get("CallSid", "default")
            
            logger.info(f"Speech result: {speech_result}")
            logger.info(f"Confidence: {confidence}")
            
            # Process speech if confidence is high enough
            if confidence > 0.1:
                # Get AI response with conversation context
                ai_response = await self.openai_client.get_response(
                    speech_result,
                    conversation_context={
                        "conversation_id": conversation_id,
                        "is_interactive": True,
                        "should_ask_questions": True,
                        "tone": "friendly",
                        "response_style": "conversational"
                    }
                )
                
                # Create response
                response = VoiceResponse()
                
                # Add natural pauses
                response.pause(length=0.5)
                response.say(ai_response, voice="alice", bargeIn="true")
                
                # Set up next speech recognition
                gather = Gather(
                    input="speech",
                    action="/twilio/speech",
                    method="POST",
                    timeout=5,
                    speechTimeout="auto",
                    language="en-US",
                    enhanced="true",
                    profanityFilter="false",
                    bargeIn="true",
                    speechModel="phone_call"
                )
                
                response.append(gather)
                
                return str(response)
            else:
                # Low confidence response with more personality
                response = VoiceResponse()
                response.pause(length=0.5)
                response.say("I'm not quite sure I caught that. Could you say it again, please?", voice="alice", bargeIn="true")
                
                gather = Gather(
                    input="speech",
                    action="/twilio/speech",
                    method="POST",
                    timeout=5,
                    speechTimeout="auto",
                    language="en-US",
                    enhanced="true",
                    profanityFilter="false",
                    bargeIn="true",
                    speechModel="phone_call"
                )
                
                response.append(gather)
                
                return str(response)
                
        except Exception as e:
            logger.error(f"Error handling speech: {str(e)}", exc_info=True)
            response = VoiceResponse()
            response.say("I'm sorry, I'm having trouble understanding. Please try again.")
            return str(response) 