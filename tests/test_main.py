import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Voice AI Agent API is running"}

def test_health():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_voice():
    """Test voice endpoint"""
    response = client.post("/voice", data={})
    assert response.status_code == 200
    assert response.text is not None
    assert len(response.text) > 0

def test_speech():
    """Test speech endpoint"""
    response = client.post("/speech", data={"SpeechResult": "Hello, how are you?"})
    assert response.status_code == 200
    assert response.text is not None
    assert len(response.text) > 0 