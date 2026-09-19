import tkinter as tk

from config import COVER_BAR, DEFAULT_VOLUME, Colors
from ui import icons
from ui.styles import fit_text, font
from ui.widgets import CircleButton, IconButton, SeekBar
from utils import format_time


class PlayerBar(tk.Frame):
    HEIGHT = 92
    TITLE_FONT = font(10, "bold")

    def __init__(self, parent, *, on_toggle_play, on_stop, on_next,
                 on_previous, on_volume_change, on_seek_start, on_seek_end):
        super().__init__(parent, bg=Colors.BLACK, height=self.HEIGHT)
        self.grid_propagate(False)

        # Same weight group on the outer columns keeps the middle centred.
        self.columnconfigure(0, weight=3, uniform="bar")
        self.columnconfigure(1, weight=4, uniform="bar")
        self.columnconfigure(2, weight=3, uniform="bar")
        self.rowconfigure(0, weight=1)

        self._full_title = ""
        self._on_volume_change = on_volume_change
        self._on_seek_start = on_seek_start
        self._on_seek_end = on_seek_end
        self._volume_before_mute = DEFAULT_VOLUME

        self._build_song_info()
        self._build_controls(on_toggle_play, on_stop, on_next, on_previous)
        self._build_volume()

    # --- Building ------------------------------------------------------
    def _build_song_info(self):
        frame = tk.Frame(self, bg=Colors.BLACK)
        frame.grid(row=0, column=0, sticky="nsew", padx=(16, 8))
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        self._cover = tk.Label(frame, bg=Colors.BLACK, bd=0)
        self._cover.grid(row=0, column=0, padx=(0, 14))

        text = tk.Frame(frame, bg=Colors.BLACK)
        text.grid(row=0, column=1, sticky="nsew")
        text.rowconfigure(0, weight=1)
        text.rowconfigure(3, weight=1)
        text.columnconfigure(0, weight=1)

        self._title = tk.Label(
            text, font=self.TITLE_FONT, fg=Colors.TEXT,
            bg=Colors.BLACK, anchor="w",
        )
        self._title.grid(row=1, column=0, sticky="w")

        self._status = tk.Label(
            text, font=font(9), fg=Colors.TEXT_MUTED,
            bg=Colors.BLACK, anchor="w",
        )
        self._status.grid(row=2, column=0, sticky="w")

        text.bind("<Configure>", self._fit_title)

    def _build_controls(self, on_toggle_play, on_stop, on_next, on_previous):
        center = tk.Frame(self, bg=Colors.BLACK)
        center.grid(row=0, column=1, sticky="ew")

        buttons = tk.Frame(center, bg=Colors.BLACK)
        buttons.pack(pady=(12, 2))

        for icon, size, command in (
            ("stop", 20, on_stop),
            ("prev", 24, on_previous),
        ):
            IconButton(
                buttons, icon, size=size, bg=Colors.BLACK, command=command
            ).pack(side="left", padx=10)

        self._play_button = CircleButton(
            buttons, "play", size=40, fill=Colors.TEXT,
            hover_fill="#F0F0F0", glyph_color=Colors.BLACK,
            bg=Colors.BLACK, command=on_toggle_play,
        )
        self._play_button.pack(side="left", padx=10)

        IconButton(
            buttons, "next", size=24, bg=Colors.BLACK, command=on_next
        ).pack(side="left", padx=10)

        progress = tk.Frame(center, bg=Colors.BLACK)
        progress.pack(fill="x", padx=8)

        self._current_time = tk.Label(
            progress, text="00:00", font=font(9), width=5, anchor="e",
            fg=Colors.TEXT_MUTED, bg=Colors.BLACK,
        )
        self._current_time.pack(side="left")

        self._progress = SeekBar(
            progress, bg=Colors.BLACK, maximum=100,
            on_press=lambda value: self._on_seek_start(),
            on_change=self._on_progress_drag,
            on_release=self._on_seek_end,
        )
        self._progress.pack(side="left", fill="x", expand=True, padx=6)

        self._total_time = tk.Label(
            progress, text="00:00", font=font(9), width=5, anchor="w",
            fg=Colors.TEXT_MUTED, bg=Colors.BLACK,
        )
        self._total_time.pack(side="left")

    def _build_volume(self):
        frame = tk.Frame(self, bg=Colors.BLACK)
        frame.grid(row=0, column=2, sticky="e", padx=(8, 24))

        self._volume_icon = IconButton(
            frame, "volume", size=20, bg=Colors.BLACK,
            command=self._toggle_mute,
        )
        self._volume_icon.pack(side="left", padx=(0, 6))

        self._volume = SeekBar(
            frame, bg=Colors.BLACK, maximum=100, value=DEFAULT_VOLUME,
            width=110, on_change=self._on_volume_drag,
        )
        self._volume.pack(side="left")

    # --- Volume --------------------------------------------------------
    def _on_volume_drag(self, value):
        self._volume_icon.set_icon("volume_mute" if value <= 0 else "volume")
        self._on_volume_change(value)

    def _toggle_mute(self):
        if self._volume.value > 0:
            self._volume_before_mute = self._volume.value
            new_value = 0
        else:
            new_value = self._volume_before_mute or DEFAULT_VOLUME

        self._volume.set_value(new_value)
        self._on_volume_drag(new_value)

    # --- Progress ------------------------------------------------------
    def _on_progress_drag(self, value):
        self._current_time.config(text=format_time(value))

    # --- Methods the app calls -----------------------------------------
    def show_track(self, title, status, cover):
        """Show a song. `cover` is an album.Cover or None."""
        photo = cover.bar if cover else icons.placeholder(COVER_BAR, 4)
        self._cover.config(image=photo)
        self._cover.image = photo

        self._full_title = title
        self._title.config(text=title)
        self._status.config(text=status)

    def set_status(self, status):
        self._status.config(text=status)

    def set_playing(self, playing):
        self._play_button.set_glyph("pause" if playing else "play")

    def set_duration(self, seconds):
        self._progress.set_range(max(seconds, 1))
        self._total_time.config(text=format_time(seconds))

    def set_position(self, seconds):
        self._progress.set_value(seconds)
        self._current_time.config(text=format_time(seconds))

    def _fit_title(self, event):
        self._title.config(
            text=fit_text(self._full_title, self.TITLE_FONT, event.width - 8)
        )