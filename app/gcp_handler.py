from google.cloud import storage, texttospeech
from app.config import settings
from app.models.audio import AudioFile
import uuid
import logging
import os

logger = logging.getLogger(__name__)

class GCPClient:
    def __init__(self):
        # Initialize storage client with explicit credentials
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not credentials_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")
            
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")
            
        try:
            self.storage_client = storage.Client.from_service_account_json(credentials_path)
            self.bucket = self.storage_client.bucket(settings.GCP_BUCKET_NAME)
            logger.info("GCP Storage client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GCP Storage client: {str(e)}")
            raise
            
        try:
            self.tts_client = texttospeech.TextToSpeechClient.from_service_account_json(credentials_path)
            self.tts_enabled = True
            logger.info("GCP Text-to-Speech client initialized successfully")
        except Exception as e:
            logger.warning(f"Text-to-Speech API not available: {str(e)}")
            self.tts_enabled = False
    
    async def text_to_speech(self, text: str) -> AudioFile:
        """Convert text to speech and store in GCP"""
        try:
            if not self.tts_enabled:
                raise Exception("Text-to-Speech API is not enabled. Please enable it in Google Cloud Console.")
            
            # Configure the text-to-speech request
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-F",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            # Perform the text-to-speech request
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Generate a unique filename
            filename = f"speech_{uuid.uuid4()}.mp3"
            
            # Upload to GCP Storage
            blob = self.bucket.blob(filename)
            blob.upload_from_string(response.audio_content, content_type="audio/mp3")
            
            # Generate a signed URL
            url = blob.generate_signed_url(
                version="v4",
                expiration=3600,  # URL expires in 1 hour
                method="GET"
            )
            
            return AudioFile(
                filename=filename,
                url=url,
                content_type="audio/mp3"
            )
            
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {str(e)}")
            # Return a fallback response
            return AudioFile(
                filename="fallback.mp3",
                url="",  # Empty URL since we'll use Twilio's TTS
                content_type="text/plain"
            ) 