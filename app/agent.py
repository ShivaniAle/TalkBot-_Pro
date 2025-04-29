import dialogflow
import uuid
from app.config import settings

class VoiceAgent:
    def __init__(self):
        self.session_client = dialogflow.SessionsClient()
        self.project_id = settings.GCP_PROJECT_ID
        self.session_id = str(uuid.uuid4())
        self.session = self.session_client.session_path(self.project_id, self.session_id) 