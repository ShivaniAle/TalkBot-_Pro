import asyncio
import logging
from typing import AsyncIterator, Optional
import wave
import numpy as np
from scipy import signal
import sounddevice as sd

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_buffer = []
        self.is_processing = False
        
    async def start_streaming(self) -> AsyncIterator[bytes]:
        """Start streaming audio input"""
        try:
            self.is_processing = True
            
            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                if self.is_processing:
                    self.audio_buffer.append(indata.copy())
            
            # Start audio stream
            stream = sd.InputStream(
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=audio_callback
            )
            
            with stream:
                while self.is_processing:
                    if self.audio_buffer:
                        # Process audio in chunks
                        chunk = self.audio_buffer.pop(0)
                        processed_chunk = self._process_audio_chunk(chunk)
                        yield processed_chunk
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"Error in audio streaming: {str(e)}")
            raise
            
    def stop_streaming(self):
        """Stop audio streaming"""
        self.is_processing = False
        
    def _process_audio_chunk(self, chunk: np.ndarray) -> bytes:
        """Process audio chunk with noise reduction and enhancement"""
        try:
            # Convert to float32
            audio_data = chunk.astype(np.float32)
            
            # Apply noise reduction
            audio_data = self._reduce_noise(audio_data)
            
            # Apply audio enhancement
            audio_data = self._enhance_audio(audio_data)
            
            # Convert back to int16 for transmission
            audio_data = (audio_data * 32767).astype(np.int16)
            
            return audio_data.tobytes()
            
        except Exception as e:
            logger.error(f"Error processing audio chunk: {str(e)}")
            raise
            
    def _reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply noise reduction to audio data"""
        try:
            # Simple noise gate
            noise_threshold = 0.02
            audio_data[np.abs(audio_data) < noise_threshold] = 0
            
            # Apply low-pass filter
            b, a = signal.butter(4, 0.8, btype='low')
            audio_data = signal.filtfilt(b, a, audio_data)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error in noise reduction: {str(e)}")
            return audio_data
            
    def _enhance_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Enhance audio quality"""
        try:
            # Normalize audio
            audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Apply slight compression
            threshold = 0.3
            ratio = 0.6
            audio_data = np.where(
                np.abs(audio_data) > threshold,
                threshold + (np.abs(audio_data) - threshold) * ratio,
                audio_data
            )
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Error in audio enhancement: {str(e)}")
            return audio_data
            
    async def save_audio(self, filename: str, duration: float):
        """Save audio to file for specified duration"""
        try:
            recorded_data = []
            
            def callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio recording status: {status}")
                recorded_data.append(indata.copy())
            
            with sd.InputStream(
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=callback
            ):
                await asyncio.sleep(duration)
            
            # Combine all recorded chunks
            audio_data = np.concatenate(recorded_data)
            
            # Save to WAV file
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
                
            logger.info(f"Audio saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving audio: {str(e)}")
            raise 