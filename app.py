from flask import Flask, render_template, jsonify, request
from modules import audio, transcribe, nlp, geo, db
import os
import soundfile

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

@app.route("/", methods=["GET"])
def retrieve():
    return render_template('layout2.html')

@app.route("/sendRequest/history", methods=["GET", "POST"])
def history():
    conn = db.open_connection('static/pdscanner.db')
    results = db.fetch_events(conn, request.args.get("start"), request.args.get("end"))
    historical_markers = [
        {
            'geometry': {'type': 'Point', 'coordinates': [row[1], row[2]]},
            'properties': {'title': row[3], 'description': row[4], 'marker-size': 'large', 'marker-color': '#FF0000', 'marker-symbol': 'police'}
        }
        for row in results
    ]
    return jsonify(map_markers=historical_markers)

@app.route("/sendRequest/newlocation", methods=["GET", "POST"])
def newlocation():
    location_to_url = {
        "portland-or": 'http://relay.broadcastify.com:80/37813088?nocache=3792733',
        "miami-fl": 'http://audio2.broadcastify.com/67440258?nocache=6895748',
        "chicago-il": 'http://audio4.broadcastify.com/il_chicago_police2?nocache=8444144',
        "seattle-wa": 'http://audio10.broadcastify.com/ctvjymw580k2?nocache=9035869'
    }
    location = request.args.get("location")
    stream_url = location_to_url.get(location, location_to_url["portland-or"])
    return "ok"

@app.route("/sendRequest/scanner", methods=["GET", "POST"])
def scan():
    stream_url = 'http://relay.broadcastify.com:80/37813088?nocache=3792733'
    mp3_path = "static/stream.mp3"
    wav_path = "static/stream.wav"
    
    audio.fetch_audio(stream_url, mp3_path)
    audio.convert_mp3_to_wav(mp3_path, wav_path)
    
    # Reduce noise
    reduced_noise_audio, sr = audio.reduce_noise(wav_path)
    soundfile.write(wav_path, reduced_noise_audio, sr)
    
    model = transcribe.load_model('models/deepspeech-0.9.3-model.pbmm')
    transcription = transcribe.transcribe_audio(model, wav_path)
    
    # CTC decoding
    logits = transcription['logits']
    sequence_length = transcription['sequence_length']
    decoded = transcribe.ctc_decode(logits, sequence_length)
    
    entities = nlp.extract_entities(decoded)
    return jsonify(transcription=decoded, entities=entities)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
