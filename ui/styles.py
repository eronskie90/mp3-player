import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from config import Colors

# The first of these that is installed gets used.
_PREFERRED_FONTS = (
    "Circular Std", "Segoe UI", "SF Pro Text",
    "Helvetica Neue", "Helvetica", "Arial",
)
_family = "Arial"
_measure_fonts = {}

SCROLLBAR_STYLE = "Spotify.Vertical.TScrollbar"


def init_styles(root):
    global _family

    available = set(tkfont.families(root))
    for name in _PREFERRED_FONTS:
        if name in available:
            _family = name
            break

    style = ttk.Style(root)
    style.theme_use("clam")

    # A thin scrollbar with no arrow buttons.
    style.layout(SCROLLBAR_STYLE, [
        ("Vertical.Scrollbar.trough", {
            "sticky": "ns",
            "children": [
                ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"}),
            ],
        }),
    ])
    style.configure(
        SCROLLBAR_STYLE,
        troughcolor=Colors.CARD,
        background=Colors.TRACK,
        bordercolor=Colors.CARD,
        lightcolor=Colors.TRACK,
        darkcolor=Colors.TRACK,
        gripcount=0,
        width=10,
        relief="flat",
    )
    style.map(
        SCROLLBAR_STYLE,
        background=[("pressed", "#9A9A9A"), ("active", "#7A7A7A")],
        lightcolor=[("pressed", "#9A9A9A"), ("active", "#7A7A7A")],
        darkcolor=[("pressed", "#9A9A9A"), ("active", "#7A7A7A")],
    )


def font(size, weight="normal"):
    """A font tuple in the app's font family."""
    return (_family, size, weight)


def fit_text(text, font_spec, max_width):
    if font_spec not in _measure_fonts:
        _measure_fonts[font_spec] = tkfont.Font(font=font_spec)
    measure = _measure_fonts[font_spec].measure

    if max_width <= 0 or measure(text) <= max_width:
        return text

    while text and measure(text + "…") > max_width:
        text = text[:-1]

    return text + "…"


def is_inside(widget, ancestor):
    name, root = str(widget), str(ancestor)
    return name == root or name.startswith(root + ".")