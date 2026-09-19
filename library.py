import os
import shutil
from collections import namedtuple

from config import AUDIO_EXTENSIONS, MUSIC_FOLDER


def song_path(filename):
    
    return os.path.join(MUSIC_FOLDER, filename)


def list_songs():
    
    return sorted(
        file
        for file in os.listdir(MUSIC_FOLDER)
        if file.lower().endswith(AUDIO_EXTENSIONS)
    )


def add_songs(paths):
    failures = []

    for path in paths:
        filename = os.path.basename(path)
        destination = song_path(filename)

        if os.path.exists(destination):
            continue

        try:
            shutil.copyfile(path, destination)
        except OSError as error:
            failures.append((filename, error))

    return failures


def delete_song(filename):
    
    try:
        os.remove(song_path(filename))
        return True
    except OSError:
        return False


Song = namedtuple("Song", "filename title format size")


def song_info(filename):
    
    try:
        size = os.path.getsize(song_path(filename))
    except OSError:
        size = 0

    title, extension = os.path.splitext(filename)

    return Song(
        filename=filename,
        title=title,
        format=extension.lstrip(".").upper(),
        size=size,
    )