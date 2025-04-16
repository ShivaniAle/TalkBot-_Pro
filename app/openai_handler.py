from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
from app.config import settings

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
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}", exc_info=True)
            raise

    async def get_response(self, user_input: str) -> str:
        """Get response from OpenAI assistant"""
        try:
            logger.info(f"Sending request to OpenAI: {user_input}")
            
            # Create a thread
            thread = self.client.beta.threads.create()
            logger.info(f"Created thread: {thread.id}")
            
            # Add message to thread
            message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_input
            )
            logger.info(f"Added message to thread: {message.id}")
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
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
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting OpenAI response: {str(e)}", exc_info=True)
            raise 