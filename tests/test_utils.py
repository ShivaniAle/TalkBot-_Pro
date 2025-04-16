import pytest
from app.utils.audio_utils import generate_unique_filename
from app.utils.storage_utils import upload_to_gcs
from datetime import datetime

def test_generate_unique_filename():
    """Test generate_unique_filename function"""
    filename = generate_unique_filename("test.mp3")
    assert filename.endswith(".mp3")
    assert "test" in filename
    assert len(filename) > len("test.mp3")

def test_upload_to_gcs():
    """Test upload_to_gcs function"""
    # This test requires a valid GCP bucket and credentials
    # It will be skipped if the environment is not set up correctly
    pytest.skip("This test requires GCP credentials and a valid bucket")
    
    # Test data
    data = b"test data"
    filename = generate_unique_filename("test.txt")
    
    # Upload the data
    url = upload_to_gcs(data, "text/plain", filename)
    
    # Check the result
    assert url is not None
    assert url.startswith("https://storage.googleapis.com/") 