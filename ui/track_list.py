import sys
import tkinter as tk
from tkinter import ttk

from config import COVER_THUMB, Colors
from ui import icons
from ui.styles import SCROLLBAR_STYLE, fit_text, font, is_inside
from ui.widgets import IconButton
from utils import format_size

ROW_HEIGHT = 56
SIDE_PADDING = 16

# Column widths (shared by the header and every row so they line up)
NUM_WIDTH = 48
THUMB_WIDTH = 52
SIZE_WIDTH = 90
ACTION_WIDTH = 44


class TrackRow(tk.Frame):
    """One song: number, cover, title, format, size, remove button."""

    TITLE_FONT = font(11, "bold")

    def __init__(self, parent, track_list, index, song, cover):
        super().__init__(parent, height=ROW_HEIGHT, bg=Colors.CARD)
        self.grid_propagate(False)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        self._list = track_list
        self.index = index
        self._full_title = song.title
        self.hovered = False
        self.selected = False
        self.current = False

        # --- number / play icon ---
        self._num_cell = tk.Frame(self, width=NUM_WIDTH, bg=Colors.CARD)
        self._num_cell.grid(row=0, column=0, sticky="ns")
        self._num_cell.pack_propagate(False)
        self._num_label = tk.Label(
            self._num_cell, text=str(index + 1), font=font(11),
            fg=Colors.TEXT_MUTED, bg=Colors.CARD,
        )
        self._num_label.pack(expand=True)

        # --- cover thumbnail ---
        thumb = cover.thumb if cover else icons.placeholder(COVER_THUMB, 4)
        self._thumb_cell = tk.Frame(self, width=THUMB_WIDTH, bg=Colors.CARD)
        self._thumb_cell.grid(row=0, column=1, sticky="ns")
        self._thumb_cell.pack_propagate(False)
        self._thumb = tk.Label(self._thumb_cell, image=thumb, bg=Colors.CARD, bd=0)
        self._thumb.image = thumb
        self._thumb.pack(expand=True, anchor="w")

        # --- title + format ---
        self._text_cell = tk.Frame(self, bg=Colors.CARD)
        self._text_cell.grid(row=0, column=2, sticky="nsew")
        self._text_cell.rowconfigure(0, weight=1)
        self._text_cell.rowconfigure(3, weight=1)
        self._text_cell.columnconfigure(0, weight=1)

        self._title = tk.Label(
            self._text_cell, text=song.title, font=self.TITLE_FONT,
            fg=Colors.TEXT, bg=Colors.CARD, anchor="w",
        )
        self._title.grid(row=1, column=0, sticky="w")

        self._subtitle = tk.Label(
            self._text_cell, text=song.format, font=font(9),
            fg=Colors.TEXT_MUTED, bg=Colors.CARD, anchor="w",
        )
        self._subtitle.grid(row=2, column=0, sticky="w")

        self._text_cell.bind("<Configure>", self._fit_title)

        # --- file size ---
        self._size_cell = tk.Frame(self, width=SIZE_WIDTH, bg=Colors.CARD)
        self._size_cell.grid(row=0, column=3, sticky="ns")
        self._size_cell.pack_propagate(False)
        self._size_label = tk.Label(
            self._size_cell, text=format_size(song.size), font=font(10),
            fg=Colors.TEXT_MUTED, bg=Colors.CARD, anchor="w",
        )
        self._size_label.pack(expand=True, fill="x")

        # --- remove button (only visible on hover) ---
        self._action_cell = tk.Frame(self, width=ACTION_WIDTH, bg=Colors.CARD)
        self._action_cell.grid(row=0, column=4, sticky="ns")
        self._action_cell.pack_propagate(False)
        self._remove = IconButton(
            self._action_cell, "trash", size=18, bg=Colors.CARD,
            command=lambda: track_list.remove(index),
        )
        self._remove.pack(expand=True)

        self._background_widgets = [
            self, self._num_cell, self._num_label, self._thumb_cell,
            self._thumb, self._text_cell, self._title, self._subtitle,
            self._size_cell, self._size_label, self._action_cell, self._remove,
        ]

        self._bind_events()
        self._apply_state()

    # --- Events --------------------------------------------------------
    def _bind_events(self):
        for widget in self._background_widgets:
            widget.bind("<Enter>", self._on_enter, add="+")
            widget.bind("<Leave>", self._on_leave, add="+")

            if widget is not self._remove:
                widget.bind("<Button-2>", self._on_menu, add="+")
                widget.bind("<Button-3>", self._on_menu, add="+")
                widget.bind("<Control-Button-1>", self._on_menu, add="+")

        # Clicking anywhere except the icons selects; double-click plays.
        for widget in self._background_widgets:
            if widget not in (self._remove, self._num_cell, self._num_label):
                widget.bind("<Button-1>", self._on_click, add="+")
                widget.bind("<Double-Button-1>", self._on_double_click, add="+")

        # Clicking the number / play icon plays right away.
        for widget in (self._num_cell, self._num_label):
            widget.bind("<Button-1>", self._on_play_click, add="+")

    def _on_enter(self, event):
        self.hovered = True
        self._apply_state()

    def _on_leave(self, event):
        # Moving between the row's own child widgets also fires <Leave>,
        # so only un-hover once the pointer is really outside the row.
        x, y = self.winfo_pointerxy()
        under_pointer = self.winfo_containing(x, y)

        if under_pointer is None or not is_inside(under_pointer, self):
            self.hovered = False
            self._apply_state()

    def _on_click(self, event):
        self._list.select(self.index)

    def _on_double_click(self, event):
        self._list.play(self.index)

    def _on_play_click(self, event):
        self._list.select(self.index)
        self._list.play(self.index)

    def _on_menu(self, event):
        self._list.select(self.index)
        self._list.show_menu(event, self.index)

    # --- Appearance ----------------------------------------------------
    def set_selected(self, selected):
        self.selected = selected
        self._apply_state()

    def set_current(self, current):
        self.current = current
        self._apply_state()

    def _apply_state(self):
        if self.selected:
            background = Colors.SELECTED
        elif self.hovered:
            background = Colors.HOVER
        else:
            background = Colors.CARD

        for widget in self._background_widgets:
            widget.config(bg=background)

        self._title.config(fg=Colors.GREEN if self.current else Colors.TEXT)

        if self.hovered:
            image = icons.icon("play", 18, Colors.TEXT)
            self._num_label.config(image=image, text="")
            self._num_label.image = image
        elif self.current:
            image = icons.icon("bars", 18, Colors.GREEN)
            self._num_label.config(image=image, text="")
            self._num_label.image = image
        else:
            self._num_label.config(image="", text=str(self.index + 1))

        self._remove.set_hidden(not self.hovered)

    def _fit_title(self, event):
        self._title.config(
            text=fit_text(self._full_title, self.TITLE_FONT, event.width - 8)
        )


class TrackList(tk.Frame):
    def __init__(self, parent, *, on_play, on_remove):
        super().__init__(parent, bg=Colors.CARD)
        self._on_play = on_play
        self._on_remove = on_remove

        self._rows = []
        self._selected = None
        self._current = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_column_header()
        self._build_canvas()
        self._build_empty_message()
        self._build_menu()

        # One global wheel binding; it checks whether the pointer is over us.
        self.bind_all("<MouseWheel>", self._on_wheel, add="+")
        self.bind_all("<Button-4>", self._on_wheel, add="+")
        self.bind_all("<Button-5>", self._on_wheel, add="+")

    # --- Building ------------------------------------------------------
    def _build_column_header(self):
        header = tk.Frame(self, bg=Colors.CARD)
        header.grid(row=0, column=0, sticky="ew", padx=SIDE_PADDING)

        row = tk.Frame(header, bg=Colors.CARD, height=36)
        row.pack(fill="x")
        row.grid_propagate(False)
        row.columnconfigure(0, minsize=NUM_WIDTH)
        row.columnconfigure(1, minsize=THUMB_WIDTH)
        row.columnconfigure(2, weight=1)
        row.columnconfigure(3, minsize=SIZE_WIDTH)
        row.columnconfigure(4, minsize=ACTION_WIDTH)
        row.rowconfigure(0, weight=1)

        def heading(text, column, sticky):
            tk.Label(
                row, text=text, font=font(9, "bold"),
                fg=Colors.TEXT_MUTED, bg=Colors.CARD, anchor="w",
            ).grid(row=0, column=column, sticky=sticky)

        heading("#", 0, "")
        heading("TITLE", 2, "w")
        heading("SIZE", 3, "w")

        tk.Frame(header, height=1, bg=Colors.DIVIDER).pack(fill="x")

    def _build_canvas(self):
        self.canvas = tk.Canvas(
            self, bg=Colors.CARD, highlightthickness=0, bd=0,
            yscrollincrement=ROW_HEIGHT // 2,
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", style=SCROLLBAR_STYLE,
            command=self.canvas.yview,
        )
        self.canvas.configure(yscrollcommand=self._on_yscroll)

        self._inner = tk.Frame(self.canvas, bg=Colors.CARD)
        self._window = self.canvas.create_window(
            (SIDE_PADDING, 0), window=self._inner, anchor="nw"
        )
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _build_empty_message(self):
        self._empty = tk.Frame(self.canvas, bg=Colors.CARD)
        tk.Label(
            self._empty, text="Your library is empty",
            font=font(16, "bold"), fg=Colors.TEXT, bg=Colors.CARD,
        ).pack()
        tk.Label(
            self._empty, text="Click “Add Song” to get started",
            font=font(11), fg=Colors.TEXT_MUTED, bg=Colors.CARD,
        ).pack(pady=(6, 0))

    def _build_menu(self):
        self._menu = tk.Menu(
            self, tearoff=0, bg=Colors.PLACEHOLDER, fg=Colors.TEXT,
            activebackground="#3E3E3E", activeforeground=Colors.TEXT,
            bd=0, relief="flat",
        )
        self._menu_index = None
        self._menu.add_command(
            label="Play", command=lambda: self.play(self._menu_index)
        )
        self._menu.add_command(
            label="Remove from library",
            command=lambda: self.remove(self._menu_index),
        )

    # --- Public API ----------------------------------------------------
    def set_tracks(self, songs, covers):
        """Rebuild the list. `songs` are library.Song tuples."""
        scroll_position = self.canvas.yview()[0]

        for row in self._rows:
            row.destroy()
        self._rows = []
        self._selected = None

        for index, song in enumerate(songs):
            cover = covers[index] if index < len(covers) else None
            row = TrackRow(self._inner, self, index, song, cover)
            row.pack(fill="x")
            self._rows.append(row)

        if self._rows:
            self._empty.place_forget()
        else:
            self._empty.place(relx=0.5, rely=0.35, anchor="center")

        self.set_current(self._current)
        self._update_scroll_region()
        self.canvas.yview_moveto(scroll_position)

    def set_current(self, index):
       
        if index is not None and index >= len(self._rows):
            index = None

        self._current = index

        for row in self._rows:
            row.set_current(row.index == index)

    def get_selected_index(self):
        return self._selected

    def see(self, index):
        
        total = len(self._rows) * ROW_HEIGHT
        view = self.canvas.winfo_height()

        if index is None or total <= view:
            return

        top = self.canvas.canvasy(0)
        row_top = index * ROW_HEIGHT
        row_bottom = row_top + ROW_HEIGHT

        if row_top < top:
            self.canvas.yview_moveto(row_top / total)
        elif row_bottom > top + view:
            self.canvas.yview_moveto((row_bottom - view) / total)

    # --- Actions used by the rows --------------------------------------
    def select(self, index):
        self._selected = index

        for row in self._rows:
            row.set_selected(row.index == index)

    def play(self, index):
        if index is not None:
            self._on_play(index)

    def remove(self, index):
        if index is not None:
            self._on_remove(index)

    def show_menu(self, event, index):
        self._menu_index = index
        try:
            self._menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._menu.grab_release()

    # --- Scrolling -----------------------------------------------------
    def _update_scroll_region(self):
        width = self.canvas.winfo_width()
        height = max(len(self._rows) * ROW_HEIGHT, self.canvas.winfo_height())
        self.canvas.configure(scrollregion=(0, 0, width, height))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self._window, width=event.width - 2 * SIDE_PADDING)
        self._update_scroll_region()

    def _on_yscroll(self, first, last):
        self.scrollbar.set(first, last)

        if float(first) <= 0.0 and float(last) >= 1.0:
            self.scrollbar.grid_remove()
        else:
            self.scrollbar.grid(row=1, column=1, sticky="ns")

    def _on_wheel(self, event):
        under_pointer = self.winfo_containing(event.x_root, event.y_root)

        if under_pointer is None or not is_inside(under_pointer, self):
            return

        if self.canvas.yview() == (0.0, 1.0):
            return

        if event.num == 4:         
            steps = -2
        elif event.num == 5:        
            steps = 2
        elif sys.platform == "darwin":
            steps = -event.delta
        else:                         
            steps = int(-event.delta / 120 * 2) or (-1 if event.delta > 0 else 1)

        self.canvas.yview_scroll(steps, "units")