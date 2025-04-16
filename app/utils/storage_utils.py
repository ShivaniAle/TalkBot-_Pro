from google.cloud import storage
from app.config import settings
import uuid
from typing import Optional

def generate_unique_filename(extension: str = "") -> str:
    """Generate a unique filename with optional extension"""
    filename = str(uuid.uuid4())
    if extension:
        filename = f"{filename}.{extension.lstrip('.')}"
    return filename

def upload_to_gcs(
    data: bytes,
    content_type: str,
    filename: Optional[str] = None
) -> Optional[str]:
    """Upload data to Google Cloud Storage and return the public URL"""
    try:
        # Initialize GCS client
        storage_client = storage.Client()
        bucket = storage_client.bucket(settings.gcp_bucket_name)
        
        # Generate filename if not provided
        if not filename:
            filename = generate_unique_filename()
        
        # Upload the file
        blob = bucket.blob(filename)
        blob.upload_from_string(
            data,
            content_type=content_type
        )
        
        # Generate signed URL
        url = blob.generate_signed_url(
            version="v4",
            expiration=3600,  # URL expires in 1 hour
            method="GET"
        )
        
        return url
        
    except Exception as e:
        print(f"Error uploading to GCS: {str(e)}")
        return None 