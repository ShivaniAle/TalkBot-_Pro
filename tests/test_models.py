import pytest
from app.models.audio import AudioFile
from app.models.conversation import Message, Conversation
from datetime import datetime

def test_audio_file():
    """Test AudioFile model"""
    audio_file = AudioFile(
        filename="test.mp3",
        url="https://example.com/test.mp3",
        content_type="audio/mp3"
    )
    assert audio_file.filename == "test.mp3"
    assert audio_file.url == "https://example.com/test.mp3"
    assert audio_file.content_type == "audio/mp3"

def test_message():
    """Test Message model"""
    message = Message(
        role="user",
        content="Hello, how are you?"
    )
    assert message.role == "user"
    assert message.content == "Hello, how are you?"
    assert isinstance(message.timestamp, datetime)

def test_conversation():
    """Test Conversation model"""
    conversation = Conversation(id="test")
    assert conversation.id == "test"
    assert conversation.messages == []
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)
    
    # Test adding a message
    conversation.add_message("user", "Hello, how are you?")
    assert len(conversation.messages) == 1
    assert conversation.messages[0].role == "user"
    assert conversation.messages[0].content == "Hello, how are you?"
    
    # Test getting the last message
    last_message = conversation.get_last_message()
    assert last_message is not None
    assert last_message.role == "user"
    assert last_message.content == "Hello, how are you?" 