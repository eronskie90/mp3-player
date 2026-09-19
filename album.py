import os
from dataclasses import dataclass

from PIL import Image, ImageTk

import imaging
from config import (
    ALBUM_FOLDER,
    COVER_BAR,
    COVER_LARGE,
    COVER_THUMB,
    IMAGE_EXTENSIONS,
)


@dataclass
class Cover:

    large: ImageTk.PhotoImage   
    bar: ImageTk.PhotoImage     
    thumb: ImageTk.PhotoImage   
    accent: tuple               


def _photo(source, size, radius):
    return ImageTk.PhotoImage(imaging.cover_image(source, size, radius))


def load_album_covers():
    """Load every image in the album folder as a Cover.

    Covers are sorted by filename, so the first cover matches the first
    song in the playlist, and so on.

    Note: call this AFTER the Tk window has been created, because
    ImageTk.PhotoImage needs an existing Tk root.
    """
    files = sorted(
        file
        for file in os.listdir(ALBUM_FOLDER)
        if file.lower().endswith(IMAGE_EXTENSIONS)
    )

    covers = []

    for file in files:
        path = os.path.join(ALBUM_FOLDER, file)

        try:
            source = Image.open(path).convert("RGB")

            covers.append(Cover(
                large=_photo(source, COVER_LARGE, 8),
                bar=_photo(source, COVER_BAR, 4),
                thumb=_photo(source, COVER_THUMB, 4),
                accent=imaging.accent_from_color(imaging.average_color(source)),
            ))
        except Exception as error:
            print(f"Could not load album cover {file}: {error}")

    return covers