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
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
                
            result = self.model.transcribe(audio_path)
            return {
                'text': result['text'],
                'segments': result.get('segments', []),
                'language': result.get('language', 'unknown')
            }
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return None

    def transcribe_audio_with_timestamps(self, audio_path):
        """
        Transcribe audio file and return text with timestamp information
        """
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
                
            result = self.model.transcribe(audio_path)
            segments = []
            
            for segment in result.get('segments', []):
                segment_dict = {
                    'text': segment['text'].strip(),
                    'start': float(segment['start']),
                    'end': float(segment['end'])
                }
                segments.append(segment_dict)
            
            return {
                'full_text': result['text'].strip(),
                'segments': segments,
                'language': result.get('language', 'unknown')
            }
        except Exception as e:
            print(f"Error transcribing audio with timestamps: {str(e)}")
            return None
