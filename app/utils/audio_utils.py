import wave
import io
from typing import Optional
from datetime import datetime
import os

def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename by adding a timestamp to the original filename
    """
    # Get the file extension
    _, ext = os.path.splitext(original_filename)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create unique filename
    unique_filename = f"{timestamp}_{original_filename}"
    
    return unique_filename

def convert_audio_format(
    audio_data: bytes,
    input_format: str = "wav",
    output_format: str = "mp3"
) -> Optional[bytes]:
    """
    Convert audio data from one format to another
    Currently supports WAV to MP3 conversion
    """
    try:
        if input_format.lower() == "wav" and output_format.lower() == "mp3":
            # Read WAV file
            with wave.open(io.BytesIO(audio_data), 'rb') as wav_file:
                # Get WAV parameters
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                frame_rate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                
                # Read audio data
                audio_frames = wav_file.readframes(n_frames)
                
                # TODO: Implement actual conversion to MP3
                # For now, return the original WAV data
                return audio_data
                
        else:
            raise ValueError(f"Unsupported conversion: {input_format} to {output_format}")
            
    except Exception as e:
        print(f"Error converting audio format: {str(e)}")
        return None 