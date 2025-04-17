from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
from app.config import settings
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        """Initialize OpenAI client with API key from environment variables"""
        try:
            # Create a new client with the v2 API configuration
            self.client = OpenAI(
                api_key=settings.openai_api_key,
                base_url="https://api.openai.com/v1"
            )
            
            # Set the v2 API header for all requests
            self.client._client.headers.update({
                "OpenAI-Beta": "assistants=v2",
                "Content-Type": "application/json"
            })
            
            self.assistant_id = settings.openai_assistant_id
            self.conversation_history = []
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}", exc_info=True)
            raise

    async def get_response(self, user_input: str, conversation_history: Optional[str] = None) -> str:
        """Get response from OpenAI assistant"""
        try:
            logger.info("Getting response from OpenAI")
            
            # Prepare the conversation context
            messages = []
            
            # Add system message to set the tone
            messages.append({
                "role": "system",
                "content": """You are a friendly and helpful AI assistant having a natural conversation over the phone. 
                Keep your responses conversational, warm, and engaging.
                Use natural language patterns and occasional conversational fillers.
                Keep responses concise but informative.
                If you're not sure about something, say so honestly.
                Remember that you're speaking to someone, so be personable.
                Use simple, clear language that's easy to understand when spoken.
                Avoid complex sentences or technical jargon.
                Be enthusiastic and show interest in the conversation."""
            })
            
            # Add conversation history if available
            if conversation_history:
                # Parse the conversation history string
                for line in conversation_history.split('\n'):
                    if line.strip():
                        role, content = line.split(':', 1)
                        messages.append({
                            "role": role.strip(),
                            "content": content.strip()
                        })
            
            # Add the current user input
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.8,  # Slightly increased for more natural responses
                max_tokens=200,   # Increased for more detailed responses
                presence_penalty=0.6,  # Encourage more diverse responses
                frequency_penalty=0.6  # Reduce repetition
            )
            
            # Extract and clean the response
            ai_response = response.choices[0].message.content.strip()
            
            # Ensure the response is appropriate for voice
            ai_response = self._format_for_voice(ai_response)
            
            logger.info(f"Generated response: {ai_response}")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error getting OpenAI response: {str(e)}")
            raise

    def _format_for_voice(self, text: str) -> str:
        """Format text to be more suitable for voice output"""
        # Remove markdown formatting
        text = text.replace('**', '').replace('*', '')
        
        # Replace common text patterns with more natural speech
        replacements = {
            '...': '.',
            'etc.': 'and so on',
            'e.g.': 'for example',
            'i.e.': 'that is',
            '&': 'and',
            '%': 'percent',
            '#': 'number',
            '@': 'at'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text

    async def get_response_from_thread(self, user_input: str) -> str:
        """Get response from OpenAI assistant using a thread"""
        try:
            logger.info(f"Sending request to OpenAI: {user_input}")
            
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Create a thread
            thread = self.client.beta.threads.create()
            logger.info(f"Created thread: {thread.id}")
            
            # Add conversation history to thread
            for message in self.conversation_history:
                self.client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role=message["role"],
                    content=message["content"]
                )
            
            # Run the assistant with specific instructions
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id,
                instructions="""You are a friendly and conversational AI assistant. 
                Keep your responses natural and engaging. 
                Use a warm, helpful tone and maintain context from previous messages.
                Keep responses concise but informative.
                If you're unsure about something, be honest about it.
                Use natural language patterns and occasional conversational fillers.
                Remember that you're speaking to someone, so be personable."""
            )
            logger.info(f"Created run: {run.id}")
            
            # Wait for completion
            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                logger.info(f"Run status: {run_status.status}")
                
                if run_status.status == 'completed':
                    break
                elif run_status.status in ['failed', 'cancelled', 'expired']:
                    raise Exception(f"Run failed with status: {run_status.status}")
                
                # Wait before checking again
                import time
                time.sleep(1)
            
            # Get the assistant's response
            messages = self.client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            # Get the last assistant message
            assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]
            if not assistant_messages:
                raise Exception("No response from assistant")
                
            response = assistant_messages[0].content[0].text.value
            logger.info(f"Received response from OpenAI: {response}")
            
            # Add assistant response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting OpenAI response: {str(e)}", exc_info=True)
            raise 