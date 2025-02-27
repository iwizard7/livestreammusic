# app.py
from flask import Flask, send_file, jsonify, render_template, request
import os
import random
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, APIC

app = Flask(__name__)

MUSIC_DIR = "music"
COVER_DIR = "static/covers"
DEFAULT_COVER = "static/default.jpg"
tracks = []
cover_cache = {}

def load_tracks():
    global tracks, cover_cache
    tracks = []
    cover_cache = {}
    os.makedirs(COVER_DIR, exist_ok=True)

    for filename in os.listdir(MUSIC_DIR):
        if filename.endswith(".mp3"):
            path = os.path.join(MUSIC_DIR, filename)
            audio = MP3(path, ID3=ID3)

            title = filename
            artist = "Unknown Artist"
            cover_path = DEFAULT_COVER

            if audio.tags:
                title = audio.tags.get(TIT2, [filename])[0]
                artist = audio.tags.get(TPE1, ["Unknown Artist"])[0]

                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        cover_filename = f"{COVER_DIR}/{filename}.jpg"
                        with open(cover_filename, "wb") as img:
                            img.write(tag.data)
                        cover_path = cover_filename
                        cover_cache[filename] = cover_path
                        break

            tracks.append({
                "filename": filename,
                "title": title,
                "artist": artist,
                "cover": f"/cover/{filename}" if cover_path != DEFAULT_COVER else DEFAULT_COVER
            })

    random.shuffle(tracks)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tracks")
def get_tracks():
    return jsonify(tracks)

@app.route("/stream/<filename>")
def stream(filename):
    path = os.path.join(MUSIC_DIR, filename)
    try:
        return send_file(path, mimetype="audio/mpeg")
    except FileNotFoundError:
        abort(404)

@app.route("/cover/<filename>")
def cover(filename):
    cover_path = cover_cache.get(filename, DEFAULT_COVER)
    return send_file(cover_path, mimetype="image/jpeg")

@app.route("/shuffle", methods=["POST"])
def shuffle_tracks():
    random.shuffle(tracks)
    return jsonify(tracks)

if __name__ == "__main__":
    load_tracks()
    app.run(host="0.0.0.0", port=8080, debug=True)