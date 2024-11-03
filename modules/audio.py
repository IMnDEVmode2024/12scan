import pydub
import requests
import time
import librosa
import soundfile
import noisereduce as nr
import numpy as np
from typing import Tuple, Optional

def fetch_audio(stream_url: str, output_path: str, max_time: int = 15) -> bool:
    """
    Fetch audio from a stream URL with timeout.
    
    Args:
        stream_url (str): URL of the audio stream
        output_path (str): Path to save the audio file
        max_time (int): Maximum time to spend downloading in seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        start_time = time.time()
        r = requests.get(stream_url, stream=True)
        r.raise_for_status()  # Raise exception for bad status codes
        
        with open(output_path, 'wb') as f:
            for block in r.iter_content(1024):
                f.write(block)
                if (time.time() - start_time) > max_time:
                    break
        return True
        
    except Exception as e:
        print(f"Error fetching audio: {str(e)}")
        return False

def convert_mp3_to_wav(mp3_path: str, wav_path: str) -> bool:
    """
    Convert MP3 file to WAV format.
    
    Args:
        mp3_path (str): Path to source MP3 file
        wav_path (str): Path for output WAV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        sound = pydub.AudioSegment.from_mp3(mp3_path)
        sound.export(wav_path, format="wav")
        return True
        
    except Exception as e:
        print(f"Error converting MP3 to WAV: {str(e)}")
        return False

def reduce_noise(audio_path: str) -> Tuple[Optional[np.ndarray], Optional[int]]:
    """
    Reduce noise in audio file using noisereduce.
    
    Args:
        audio_path (str): Path to audio file
        
    Returns:
        tuple: (reduced_noise_audio, sample_rate) or (None, None) if failed
    """
    try:
        # Load audio file using librosa
        audio, sr = librosa.load(audio_path, sr=None)
        
        # Perform noise reduction
        reduced_noise_audio = nr.reduce_noise(
            y=audio, 
            sr=sr,
            stationary=True,
            prop_decrease=0.75
        )
        
        return reduced_noise_audio, sr
        
    except Exception as e:
        print(f"Error reducing noise: {str(e)}")
        return None, None

def record_audio(output_path: str) -> bool:
    """
    Record audio from the microphone.
    
    Args:
        output_path (str): Path to save the recorded audio file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Open the microphone
        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)
        
        print("Recording...")
        frames = []
        
        while True:
            data = stream.read(1024)
            frames.append(data)
            
            # Save the recorded data to a WAV file
            wf = wave.open(output_path, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Break the loop after 5 seconds
            if len(frames) >= 5 * 44100 // 1024:
                break
        
        # Close the microphone
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        return True
        
    except Exception as e:
        print(f"Error recording audio: {str(e)}")
        return False