# App.py

from flask import Flask, request, jsonify, send_file
from init import speech_to_speech, text_to_speech
import tempfile

app = Flask(__name__)

# test route lol
@app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200

@app.route('/t2s', methods=['POST'])
def t2s():
    data = request.get_json()
    text = data.get('text')
    src_lang = data.get('src_lang')
    tgt_lang = data.get('tgt_lang')
    if not all([text, src_lang, tgt_lang]):
        return jsonify({'error': 'Missing parameters'}), 400
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        text_to_speech(text, src_lang, tgt_lang, temp.name)
        temp.seek(0)
        return send_file(temp.name, as_attachment=True, download_name="translated_text_audio.wav", mimetype='audio/wav')


@app.route('/s2s', methods=['POST'])
def s2s():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    tgt_lang = request.form.get('tgt_lang')
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and tgt_lang:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
            file.save(temp.name)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_temp:
                speech_to_speech(temp.name, tgt_lang, output_temp.name)
                output_temp.seek(0)
                return send_file(output_temp.name, as_attachment=True, download_name="translated_speech_audio.wav", mimetype='audio/wav')
    else:
        return jsonify({'error': 'Missing parameters'}), 400

if __name__ == '__main__':
    app.run(debug=True)