from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import re
import json
import os

app = Flask(__name__)
CORS(app)  # Autorise tous les domaines à appeler ton API

def extract_video_id(url):
    if not url:
        return None
    url = url.strip()
    pattern = r'(?:v=|youtu\\.be/|embed/|watch\\?v=)([\\w-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.route('/', methods=['GET'])
def home():
    return "Bienvenue sur mon API de transcription YouTube hébergée sur Render !", 200

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({"success": False, "error": "No URL provided"}), 400

        video_id = extract_video_id(url)

        if not video_id:
            return jsonify({"success": False, "error": "Invalid YouTube URL"}), 400

        # Récupérer la transcription
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['fr', 'en'])
        full_transcription = ' '.join([entry['text'] for entry in transcript_list])

        # Pas d'enregistrement local de fichier JSON car Render est en serveur stateless
        return jsonify({
            "success": True,
            "transcription": full_transcription,
            "video_id": video_id
        }), 200

    except Exception as e:
        # Retourner 200 même en cas d'erreur pour que n8n continue
        return jsonify({
            "success": False,
            "transcription": None,
            "error": str(e)
        }), 200

if __name__ == '__main__':
    # Render attend que ton app Flask écoute sur '0.0.0.0' et prenne le port fourni par l'environnement
    port = int(os.environ.get('PORT', 10000))  # Par défaut 10000 si PORT non trouvé (utile pour tests locaux)
    app.run(host='0.0.0.0', port=port)
