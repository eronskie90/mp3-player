import tkinter as tk

from config import DEFAULT_ACCENT, PLAYLIST_TITLE, Colors
from ui import icons
from ui.styles import font
from ui.track_list import TrackList
from ui.widgets import CircleButton, PillButton
from utils import blend, hex_to_rgb, rgb_to_hex


class PlaylistHeader(tk.Canvas):
    STRIPS = 42
    MARGIN = 28
    # (banner height, cover tile size, title font size)
    FULL = (210, 152, 40)
    COMPACT = (150, 96, 28)

    def __init__(self, parent):
        super().__init__(
            parent, bg=Colors.CARD, highlightthickness=0, bd=0,
            height=self.FULL[0],
        )
        self._compact = False
        self._height = self.FULL[0]
        self._accent = DEFAULT_ACCENT

        self._strips = [
            self.create_rectangle(0, 0, 1, 1, width=0) for _ in range(self.STRIPS)
        ]
        self._tile = self.create_image(0, 0, anchor="sw")
        self._label = self.create_text(
            0, 0, text="PLAYLIST", anchor="w",
            font=font(9, "bold"), fill=Colors.TEXT,
        )
        self._title = self.create_text(
            0, 0, text=PLAYLIST_TITLE, anchor="w", fill=Colors.TEXT,
        )
        self._count = self.create_text(
            0, 0, text="0 songs", anchor="w",
            font=font(10), fill=Colors.TEXT,
        )

        self._arrange()
        self._recolor()
        self.bind("<Configure>", self._on_configure)

    def set_compact(self, compact):
        if compact != self._compact:
            self._compact = compact
            self._arrange()

    def _arrange(self):
        """Position everything for the current (full or compact) size."""
        height, tile, title_size = self.COMPACT if self._compact else self.FULL
        self._height = height
        self.config(height=height)

        photo = icons.tile(tile, 6)
        self.itemconfig(self._tile, image=photo)
        self.coords(self._tile, self.MARGIN, height - self.MARGIN)

        top = height - self.MARGIN - tile
        text_x = self.MARGIN + tile + 24
        self.coords(self._label, text_x, top + tile * 0.21)
        self.coords(self._title, text_x, top + tile * 0.55)
        self.coords(self._count, text_x, top + tile * 0.87)
        self.itemconfig(self._title, font=font(title_size, "bold"))

        self._layout_strips(self.winfo_width())

    def _on_configure(self, event):
        self._layout_strips(event.width)

    def _layout_strips(self, width):
        step = self._height / self.STRIPS

        for i, strip in enumerate(self._strips):
            self.coords(strip, 0, i * step, max(width, 1), (i + 1) * step + 1)

    def _recolor(self):
        card = hex_to_rgb(Colors.CARD)

        for i, strip in enumerate(self._strips):
            amount = (i / (self.STRIPS - 1)) ** 0.85
            self.itemconfig(strip, fill=rgb_to_hex(blend(self._accent, card, amount)))

    def set_accent(self, rgb):
        if rgb != self._accent:
            self._accent = rgb
            self._recolor()

    def set_count(self, count):
        self.itemconfig(self._count, text=f"{count} song{'' if count == 1 else 's'}")


class PlaylistPanel(tk.Frame):
    def __init__(self, parent, *, on_play_index, on_toggle_play,
                 on_add, on_remove):
        super().__init__(parent, bg=Colors.CARD)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._header = PlaylistHeader(self)
        self._header.grid(row=0, column=0, sticky="ew")

        toolbar = tk.Frame(self, bg=Colors.CARD)
        toolbar.grid(row=1, column=0, sticky="ew", padx=28, pady=(18, 10))

        self._play_button = CircleButton(
            toolbar, "play", size=56, fill=Colors.GREEN,
            hover_fill=Colors.GREEN_HOVER, glyph_color=Colors.BLACK,
            bg=Colors.CARD, command=on_toggle_play,
        )
        self._play_button.pack(side="left")

        PillButton(toolbar, "+  Add Song", command=on_add).pack(
            side="left", padx=(20, 0)
        )

        self._track_list = TrackList(
            self, on_play=on_play_index, on_remove=on_remove
        )
        self._track_list.grid(row=2, column=0, sticky="nsew")

        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        # Shrink the banner when the window is short.
        self._header.set_compact(event.height < 560)

    # --- Methods the app calls -----------------------------------------
    def set_songs(self, songs, covers):
        self._header.set_count(len(songs))
        self._track_list.set_tracks(songs, covers)

    def set_accent(self, rgb):
        self._header.set_accent(rgb)

    def set_playing(self, playing):
        self._play_button.set_glyph("pause" if playing else "play")

    def set_current(self, index):
        self._track_list.set_current(index)

    def see(self, index):
        self._track_list.see(index)

    def get_selected_index(self):
        return self._track_list.get_selected_index()