import os
import warnings
from flask import Flask, render_template, jsonify, request, Response # type: ignore
from modules import audio, transcribe, nlp
from modules.geo import GeoLocator
import soundfile # type: ignore
from modules import db
import pyaudio
import wave
import librosa # type: ignore
import numpy as np

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU usage

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

# Initialize components
transcriber = transcribe.WhisperTranscriber(model_name="base")
nlp_processor = nlp.NLPProcessor()
geo_locator = GeoLocator()

# Set up PyAudio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"


@app.route("/", methods=["GET"])
def retrieve():
    return render_template('layout2.html')

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        if not file.filename:
            return jsonify({'error': 'No selected file'}), 400

        temp_path = os.path.join('static', 'temp_audio.wav')
        file.save(temp_path)
        
        # Reduce noise
        reduced_noise_audio, sr = audio.reduce_noise(temp_path)
        if reduced_noise_audio is not None:
            soundfile.write(temp_path, reduced_noise_audio, sr)
        
        # Transcribe
        transcription = transcriber.transcribe_audio_with_timestamps(temp_path)
        if not transcription:
            return jsonify({'error': 'Transcription failed'}), 500
        
        # Extract entities using NLP processor
        entities = nlp_processor.extract_entities(transcription['full_text'])
        
        # Get locations using new GeoLocator
        try:
            locations = geo_locator.locate_entities(entities)
        except Exception as e:
            print(f"Geocoding error: {str(e)}")
            locations = []
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        # Format the response
        response = {
            'transcription': {
                'full_text': transcription['full_text'],
              'segments': [
                    {
                        'text': seg['text'],
                       'start': seg['start'],
                        'end': seg['end']
                    } for seg in transcription['segments']
                ],
                'language': transcription['language']
            },
            'entities': entities,
            'locations': locations
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Transcription error: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route("/stream", methods=["POST"])
def process_stream():
    try:
        data = request.get_json()
        stream_url = data.get('stream_url')
        if not stream_url:
            return jsonify({'error': 'No stream URL provided'}), 400
            
        temp_mp3 = os.path.join('static', 'temp_audio.mp3')
        temp_wav = os.path.join('static', 'temp_audio.wav')
        
        # Fetch and process audio
        if not audio.fetch_audio(stream_url, temp_mp3):
            return jsonify({'error': 'Failed to fetch audio'}), 500
            
        if not audio.convert_mp3_to_wav(temp_mp3, temp_wav):
            return jsonify({'error': 'Failed to convert audio'}), 500
            
        # Reduce noise
        reduced_noise_audio, sr = audio.reduce_noise(temp_wav)
        if reduced_noise_audio is not None:
            soundfile.write(temp_wav, reduced_noise_audio, sr)
        
        # Transcribe
        transcription = transcriber.transcribe_audio_with_timestamps(temp_wav)
        if not transcription:
            return jsonify({'error': 'Transcription failed'}), 500
        
        # Extract entities and locations using new processors
        entities = nlp_processor.extract_entities(transcription['full_text'])
        locations = geo_locator.locate_entities(entities)
        
        # Clean up
        for temp_file in [temp_mp3, temp_wav]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        # Format the response
        response = {
            'transcription': {
                'full_text': transcription['full_text'],
             'segments': [
                    {
                        'text': seg['text'],
                       'start': seg['start'],
                        'end': seg['end']
                    } for seg in transcription['segments']
                ],
                'language': transcription['language']
            },
            'entities': entities,
            'locations': locations
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Stream processing error: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route("/record_audio_from_mic", methods=["GET"])
def record_audio_from_mic():
    try:
        # Start the audio recording
        threading.Thread(target=record_audio).start()
        return jsonify({'message': 'Recording started'})
    except Exception as e:
        print(f"Error starting recording: {str(e)}")
        return jsonify({'error': f'Failed to start recording: {str(e)}'}), 500


@app.route("/record_audio", methods=["POST"])
def record_audio():
    try:
        # Open the microphone
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("Recording...")
        frames = []
        chunk_counter = 0

        while True:
            data = stream.read(CHUNK)
            frames.append(data)

            # Process the audio chunk every 30 seconds
            if len(frames) >= CHUNK_SIZE * RATE / CHUNK:
                chunk_counter += 1
                chunk = b"".join(frames)
                frames = []

                # Save the chunk to a temporary file
                temp_path = os.path.join('static', f'temp_audio_{chunk_counter}.wav')
                wf = wave.open(temp_path, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(chunk)
                wf.close()

                # Transcribe the chunk
                transcription = transcriber.transcribe_audio_with_timestamps(temp_path)

                # Extract entities and locations
                entities = nlp_processor.extract_entities(transcription['full_text'])
                locations = geo_locator.locate_entities(entities)

                # Update the dashboard
                response = {
                    'transcription': transcription,
                    'entities': entities,
                    'locations': locations
                }
                return jsonify(response)

    except Exception as e:
        print(f"Error recording audio: {str(e)}")
        return jsonify({'error': f'Failed to record audio: {str(e)}'}), 500

@app.route("/sendRequest/history", methods=["GET"])
def history():
    try:
        conn = db.open_connection('static/pdscanner.db')
        results = db.fetch_events(conn, request.args.get("start"), request.args.get("end"))
        historical_markers = [
            {
                'geometry': {'type': 'Point', 'coordinates': [row[1], row[2]]},
                'properties': {'title': row[3], 'description': row[4]}
            }
            for row in results
        ]
        return jsonify(map_markers=historical_markers)
    except Exception as e:
        print(f"History retrieval error: {str(e)}")
        return jsonify({'error': f'Failed to retrieve history: {str(e)}'}), 500

if __name__ == "__main__":
    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)
    app.run(debug=True)