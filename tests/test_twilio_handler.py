import pytest
from app.twilio_handler import TwilioHandler
from app.config import settings

@pytest.mark.asyncio
async def test_twilio_handler_initialization():
    """Test Twilio handler initialization"""
    handler = TwilioHandler()
    assert handler.account_sid == settings.twilio_account_sid
    assert handler.auth_token == settings.twilio_auth_token
    assert handler.phone_number == settings.twilio_phone_number

@pytest.mark.asyncio
async def test_twilio_handle_voice():
    """Test handling voice call"""
    handler = TwilioHandler()
    form_data = {}
    response = await handler.handle_voice(form_data)
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_twilio_handle_speech():
    """Test handling speech result"""
    handler = TwilioHandler()
    form_data = {"SpeechResult": "Hello, how are you?"}
    response = await handler.handle_speech(form_data, None)
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0 