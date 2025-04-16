import pytest
from app.openai_handler import OpenAIClient
from app.config import settings

@pytest.mark.asyncio
async def test_openai_client_initialization():
    """Test OpenAI client initialization"""
    client = OpenAIClient()
    assert client.client is not None
    assert client.assistant_id == settings.openai_assistant_id

@pytest.mark.asyncio
async def test_openai_get_response():
    """Test getting response from OpenAI"""
    client = OpenAIClient()
    response = await client.get_response("Hello, how are you?")
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0 