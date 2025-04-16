import pytest
from app.gcp_handler import GCPClient
from app.config import settings

@pytest.mark.asyncio
async def test_gcp_client_initialization():
    """Test GCP client initialization"""
    client = GCPClient()
    assert client.storage_client is not None
    assert client.bucket is not None
    assert client.bucket.name == settings.gcp_bucket_name

@pytest.mark.asyncio
async def test_gcp_text_to_speech():
    """Test text-to-speech conversion"""
    client = GCPClient()
    text = "Hello, how are you?"
    audio_file = await client.text_to_speech(text)
    assert audio_file is not None
    assert audio_file.filename is not None
    assert audio_file.url is not None
    assert audio_file.content_type is not None 