from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import re
import os

app = Flask(__name__)
CORS(app)

def extract_video_id(url):
    if not url:
        return None
    url = url.strip()

    # CORRECT : 1 seul \ et plusieurs patterns acceptés
    patterns = [
        r'(?:v=)([0-9A-Za-z_-]{11})',            # pour https://www.youtube.com/watch?v=xxx
        r'(?:youtu\.be/)([0-9A-Za-z_-]{11})',     # pour https://youtu.be/xxx
        r'(?:embed/)([0-9A-Za-z_-]{11})'          # pour https://youtube.com/embed/xxx
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None

@app.route('/', methods=['GET'])
def home():
    return "Bienvenue sur mon API Transcription YouTube hébergée sur Render !", 200

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

        return jsonify({
            "success": True,
            "transcription": full_transcription,
            "video_id": video_id
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "transcription": None
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
