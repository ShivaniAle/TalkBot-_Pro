import logging
from typing import Optional, Callable, Awaitable
from app.openai_handler import OpenAIClient

logger = logging.getLogger(__name__)

class AIHandler:
    def __init__(self):
        self._client: Optional[OpenAIClient] = None
        self._response_handler: Optional[Callable[[str], Awaitable[str]]] = None

    def initialize(self) -> bool:
        """Initialize the AI handler"""
        try:
            logger.info("Initializing AI handler...")
            self._client = OpenAIClient()
            logger.info("AI handler initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize AI handler: {str(e)}", exc_info=True)
            self._client = None
            return False

    async def get_response(self, text: str) -> str:
        """Get response from AI"""
        if not self._client:
            logger.error("AI client not initialized")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later."
        
        try:
            return await self._client.get_response(text)
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}", exc_info=True)
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later."

# Create a global instance
ai_handler = AIHandler() 