import whisper
import torch
import os

class WhisperTranscriber:
    def __init__(self, model_name="base"):
        """
        Initialize Whisper model
        model_name can be one of: "tiny", "base", "small", "medium", "large"
        """
        self.model = whisper.load_model(model_name)
        
    def transcribe_audio(self, audio_path):
        """
        Transcribe audio file using Whisper
        """
        try:
            # Load audio and pad/trim it to fit 30 seconds
            result = self.model.transcribe(audio_path)
            return {
                'text': result['text'],
                'segments': result['segments'],
                'language': result['language']
            }
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return None

    def transcribe_audio_with_timestamps(self, audio_path):
        """
        Transcribe audio file and return text with timestamp information
        """
        try:
            result = self.model.transcribe(audio_path)
            segments = []
            
            for segment in result['segments']:
                segments.append({
                    'text': segment['text'],
                    'start': segment['start'],
                    'end': segment['end'],
                    'confidence': segment['confidence']
                })
            
            return {
                'full_text': result['text'],
                'segments': segments,
                'language': result['language']
            }
        except Exception as e:
            print(f"Error transcribing audio with timestamps: {str(e)}")
            return None