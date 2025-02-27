from flask import Flask, send_file, jsonify, render_template, request
import os
import random
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, APIC

app = Flask(__name__)

MUSIC_DIR = "music"  # Папка с музыкой
COVER_DIR = "static/covers"  # Папка для обложек
DEFAULT_COVER = "static/default.jpg"  # Заглушка, если нет обложки
tracks = []


def load_tracks():
    """Загружает список MP3-файлов и их метаданные"""
    global tracks
    tracks = []
    os.makedirs(COVER_DIR, exist_ok=True)  # Создаем папку для обложек

    for filename in os.listdir(MUSIC_DIR):
        if filename.endswith(".mp3"):
            path = os.path.join(MUSIC_DIR, filename)
            audio = MP3(path, ID3=ID3)

            title = filename  # По умолчанию - имя файла
            artist = "Unknown Artist"
            cover_path = DEFAULT_COVER  # Заглушка для обложки

            if audio.tags:
                title = audio.tags.get(TIT2, [filename])[0]  # Берем ID3-тег, если есть
                artist = audio.tags.get(TPE1, ["Unknown Artist"])[0]

                # Проверяем обложку
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):  # Если есть обложка
                        cover_filename = f"{COVER_DIR}/{filename}.jpg"
                        with open(cover_filename, "wb") as img:
                            img.write(tag.data)
                        cover_path = cover_filename
                        break  # Остановить после первой найденной обложки

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
    """Стриминг MP3-файла"""
    path = os.path.join(MUSIC_DIR, filename)
    return send_file(path, mimetype="audio/mpeg")


@app.route("/cover/<filename>")
def cover(filename):
    """Возвращает обложку альбома"""
    cover_path = os.path.join(COVER_DIR, f"{filename}.jpg")
    if os.path.exists(cover_path):
        return send_file(cover_path, mimetype="image/jpeg")
    return send_file(DEFAULT_COVER, mimetype="image/jpeg")


@app.route("/shuffle", methods=["POST"])
def shuffle_tracks():
    """Перемешивает треки"""
    random.shuffle(tracks)
    return jsonify(tracks)


if __name__ == "__main__":
    load_tracks()
    app.run(host="0.0.0.0", port=8080, debug=True)
