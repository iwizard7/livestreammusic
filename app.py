from flask import Flask, send_file, jsonify, render_template, request
import os
import random
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1

app = Flask(__name__)

MUSIC_DIR = "music"  # Папка с музыкой
tracks = []  # Список треков


def load_tracks():
    """Загружает список MP3-файлов и их метаданные"""
    global tracks
    tracks = []
    for filename in os.listdir(MUSIC_DIR):
        if filename.endswith(".mp3"):
            path = os.path.join(MUSIC_DIR, filename)
            audio = MP3(path, ID3=ID3)
            title = filename  # По умолчанию - имя файла
            artist = "Unknown Artist"

            if audio.tags:
                title = audio.tags.get(TIT2, filename).text[0] if TIT2 in audio.tags else filename
                artist = audio.tags.get(TPE1, "Unknown Artist").text[0] if TPE1 in audio.tags else "Unknown Artist"

            tracks.append({"filename": filename, "title": title, "artist": artist})

    random.shuffle(tracks)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tracks")
def get_tracks():
    return jsonify(tracks)


@app.route("/stream/<filename>")
def stream(filename):
    """Стриминг MP3-файла"""
    path = os.path.join(MUSIC_DIR, filename)
    return send_file(path, mimetype="audio/mpeg")


@app.route("/shuffle", methods=["POST"])
def shuffle_tracks():
    """Перемешивает треки"""
    random.shuffle(tracks)
    return jsonify(tracks)


if __name__ == "__main__":
    load_tracks()
    app.run(host="0.0.0.0", port=8080, debug=True)
