import os
import logging
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        """Initialize the OpenAI client"""
        try:
            logger.info("Initializing OpenAI client...")
            
            # Validate required settings
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not set in environment variables")
            
            # Initialize the OpenAI client
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Store conversation history
            self.conversation_history = {}
            
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}", exc_info=True)
            raise

    async def get_response(self, user_input: str, conversation_context: dict = None) -> str:
        """Get AI response with conversation context"""
        try:
            logger.info(f"Getting response for: {user_input}")
            
            # Get or create conversation history
            conversation_id = conversation_context.get("conversation_id", "default")
            if conversation_id not in self.conversation_history:
                self.conversation_history[conversation_id] = []
            
            # Add user message to history
            self.conversation_history[conversation_id].append({"role": "user", "content": user_input})
            
            # Prepare conversation context
            if conversation_context is None:
                conversation_context = {
                    "is_interactive": True,
                    "should_ask_questions": True,
                    "tone": "friendly",
                    "response_style": "conversational"
                }
            
            # Create system message with context
            system_message = {
                "role": "system",
                "content": f"""You are a friendly and engaging conversational AI assistant having a natural phone conversation. 
                Keep your responses natural and interactive.
                {f"Tone: {conversation_context.get('tone', 'friendly')}"}
                {f"Response style: {conversation_context.get('response_style', 'conversational')}"}
                {f"Ask questions: {'Yes' if conversation_context.get('should_ask_questions', True) else 'No'}"}
                
                Important rules:
                1. Maintain context from previous messages
                2. Use natural conversational language
                3. Show genuine interest in the conversation
                4. Ask relevant follow-up questions
                5. Use conversational fillers like "hmm", "well", "you know" appropriately
                6. Keep responses concise but engaging
                7. Reference previous topics when relevant
                8. Use a warm, friendly tone throughout"""
            }
            
            # Prepare messages with history
            messages = [system_message]
            messages.extend(self.conversation_history[conversation_id][-5:])  # Keep last 5 exchanges
            
            # Get response from OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.8,  # Slightly higher temperature for more natural responses
                max_tokens=150
            )
            
            # Extract and store assistant's response
            ai_response = response.choices[0].message.content
            self.conversation_history[conversation_id].append({"role": "assistant", "content": ai_response})
            
            logger.info(f"Generated response: {ai_response}")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}", exc_info=True)
            return "I'm having trouble processing that. Could you please try again?"
            
    def set_interrupted(self, interrupted: bool = True):
        """Set interruption flag"""
        self.interrupted = interrupted 