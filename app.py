from flask import Flask, render_template, request, jsonify, send_file
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_info', methods=['POST'])
def get_info():
    url = request.json.get('url')
    try:
        yt = YouTube(url)
        return jsonify({
            'title': yt.title,
            'thumbnail': yt.thumbnail_url,
            'streams': [f"{s.resolution}" for s in yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/download/mp3', methods=['POST'])
def download_mp3():
    url = request.form.get('url')
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        temp_dir = tempfile.mkdtemp()
        stream = yt.streams.filter(only_audio=True).first()
        out_file = stream.download(output_path=temp_dir)
        base, _ = os.path.splitext(out_file)
        mp3_file = base + '.mp3'
        os.rename(out_file, mp3_file)
        return send_file(mp3_file, as_attachment=True)
    except Exception as e:
        return str(e), 500

@app.route('/download/mp4', methods=['POST'])
def download_mp4():
    url = request.form.get('url')
    quality = request.form.get('quality', '360p')
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        temp_dir = tempfile.mkdtemp()
        stream = yt.streams.filter(res=quality, progressive=True, file_extension='mp4').first()
        if not stream:
            stream = yt.streams.get_highest_resolution()
        file_path = stream.download(output_path=temp_dir)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
