from google.cloud import dialogflow_v2 as dialogflow
import uuid
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class DialogflowClient:
    def __init__(self):
        """Initialize the Dialogflow client"""
        try:
            logger.info("Initializing Dialogflow client...")
            
            # Validate required settings
            if not settings.GCP_PROJECT_ID:
                raise ValueError("GCP_PROJECT_ID is not set in environment variables")
            
            self.project_id = settings.GCP_PROJECT_ID
            self.session_id = str(uuid.uuid4())
            
            # Initialize the Dialogflow client
            self.client = dialogflow.SessionsClient()
            self.session = self.client.session_path(self.project_id, self.session_id)
            
            logger.info("Dialogflow client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Dialogflow client: {str(e)}", exc_info=True)
            raise

    async def detect_intent(self, text: str) -> str:
        """Detect intent from text input"""
        try:
            # Create the text input
            text_input = dialogflow.TextInput(text=text, language_code="en-US")
            query_input = dialogflow.QueryInput(text=text_input)
            
            # Make the request
            response = await self.client.detect_intent(
                request={"session": self.session, "query_input": query_input}
            )
            
            # Return the fulfillment text
            return response.query_result.fulfillment_text
            
        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}", exc_info=True)
            raise 