from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)
CORS(app)

def extract_video_id(url):
    pattern = r'(?:v=|youtu\\.be/|embed/)([\\w-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['fr', 'en'])
        full_transcription = ' '.join(segment['text'] for segment in transcript_list)
        return jsonify({"transcription": full_transcription})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)