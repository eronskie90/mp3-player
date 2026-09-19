import tkinter as tk

from config import COVER_LARGE, Colors
from ui import icons
from ui.styles import font


class NowPlayingPanel(tk.Frame):
    WIDTH = 320
    PADDING = 28

    def __init__(self, parent):
        super().__init__(parent, bg=Colors.CARD, width=self.WIDTH)
        self.pack_propagate(False)

        tk.Label(
            self, text="Now Playing", font=font(13, "bold"),
            fg=Colors.TEXT, bg=Colors.CARD,
        ).pack(anchor="w", padx=self.PADDING, pady=(24, 18))

        self._cover = tk.Label(self, bg=Colors.CARD, bd=0)
        self._cover.pack(anchor="w", padx=self.PADDING)

        self._title = tk.Label(
            self, font=font(20, "bold"), fg=Colors.TEXT, bg=Colors.CARD,
            anchor="w", justify="left",
            wraplength=self.WIDTH - 2 * self.PADDING,
        )
        self._title.pack(fill="x", padx=self.PADDING, pady=(22, 4))

        self._status = tk.Label(
            self, font=font(11), fg=Colors.TEXT_MUTED, bg=Colors.CARD,
            anchor="w",
        )
        self._status.pack(fill="x", padx=self.PADDING)

    def show_track(self, title, status, cover):
       
        photo = cover.large if cover else icons.placeholder(COVER_LARGE, 8)
        self._cover.config(image=photo)
        self._cover.image = photo

        self._title.config(text=title)
        self._status.config(text=status)

    def set_status(self, status):
        self._status.config(text=status)