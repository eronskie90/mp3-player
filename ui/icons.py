from PIL import Image, ImageTk

import imaging
from config import Colors

_cache = {}


def _cached(key, make_image):
    if key not in _cache:
        _cache[key] = ImageTk.PhotoImage(make_image())
    return _cache[key]


def icon(name, size, color):
    return _cached(
        ("icon", name, size, color),
        lambda: imaging.draw_icon(name, size, color),
    )


def circle(glyph, size, fill, glyph_color, scale=0.62):
    return _cached(
        ("circle", glyph, size, fill, glyph_color, scale),
        lambda: imaging.circle_image(glyph, size, fill, glyph_color, scale),
    )


def pill(width, height, fill=None, border=None):
    return _cached(
        ("pill", width, height, fill, border),
        lambda: imaging.pill_image(width, height, fill, border),
    )


def placeholder(size, radius=4):
    return _cached(
        ("placeholder", size, radius),
        lambda: imaging.placeholder_image(
            size, radius, Colors.PLACEHOLDER, Colors.TEXT_SUBTLE
        ),
    )


def tile(size, radius=6):
    return _cached(
        ("tile", size, radius),
        lambda: imaging.tile_image(size, radius, (79, 70, 229), (167, 139, 250)),
    )


def blank(size):
    return _cached(
        ("blank", size),
        lambda: Image.new("RGBA", (size, size), (0, 0, 0, 0)),
    )