from pydantic import BaseModel

class AudioFile(BaseModel):
    """Model for audio files stored in GCP"""
    filename: str
    url: str
    content_type: str 