from google.cloud import storage
import os
from app.config import settings

# Initialize the client with project from settings
client = storage.Client(project=settings.GCP_PROJECT_ID)

# Get bucket name from environment or use default
bucket_name = os.getenv("GCS_BUCKET_NAME", "challenge-voice-agent")
bucket = client.bucket(bucket_name)

def upload_to_gcs(data, blob_name, is_text=False):
    """
    Upload data to Google Cloud Storage
    :param data: The data to upload (file path or string content)
    :param blob_name: The name to give the file in GCS
    :param is_text: Whether the data is text content (True) or a file path (False)
    """
    blob = bucket.blob(blob_name)
    if is_text:
        blob.upload_from_string(data)
    else:
        blob.upload_from_filename(data)