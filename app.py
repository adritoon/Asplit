from flask import Flask, request, jsonify, send_from_directory
from spleeter_processing import process_audio
import os
import uuid

app = Flask(__name__)
RESULTS_FOLDER = "static/results"
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return "🟢 API de separación de audio con Spleeter funcionando."

@app.route('/separate', methods=['POST'])
def separate_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'Archivo no enviado'}), 400

    file = request.files['file']
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join("temp", filename)
    os.makedirs("temp", exist_ok=True)
    file.save(file_path)

    # Parámetros del usuario
    spleeter_mode = request.form.get("mode", "spleeter:2stems")
    segment_minutes = int(request.form.get("segment", 5))
    output_format = request.form.get("format", "mp3")

    try:
        zip_path = process_audio(file_path, spleeter_mode, segment_minutes, output_format)
        download_link = f"/download/{os.path.basename(zip_path)}"
        return jsonify({'download_url': download_link})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(RESULTS_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
