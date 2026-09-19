import tkinter as tk
from tkinter import font as tkfont

from config import Colors
from ui import icons
from ui.styles import font


def _clicked_inside(widget, event):
    return 0 <= event.x < widget.winfo_width() and 0 <= event.y < widget.winfo_height()


class IconButton(tk.Label):

    def __init__(self, parent, icon, *, size=20, color=Colors.TEXT_MUTED,
                 hover_color=Colors.TEXT, bg=Colors.CARD, command=None):
        super().__init__(
            parent, bg=bg, bd=0, highlightthickness=0,
            cursor="hand2", takefocus=0,
        )
        self._icon = icon
        self._size = size
        self._color = color
        self._hover_color = hover_color
        self._command = command
        self._hovered = False
        self._hidden = False

        self._refresh()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _refresh(self):
        if self._hidden:
            self.config(image=icons.blank(self._size))
        else:
            color = self._hover_color if self._hovered else self._color
            self.config(image=icons.icon(self._icon, self._size, color))

    def set_icon(self, icon):
        self._icon = icon
        self._refresh()

    def set_hidden(self, hidden):
        """Hide the icon but keep its space (so layouts don't jump)."""
        self._hidden = hidden
        self._refresh()

    def _on_enter(self, event):
        self._hovered = True
        self._refresh()

    def _on_leave(self, event):
        self._hovered = False
        self._refresh()

    def _on_release(self, event):
        if self._command and not self._hidden and _clicked_inside(self, event):
            self._command()


class CircleButton(tk.Label):
    """A round button with an icon inside (the big play button)."""

    def __init__(self, parent, glyph, *, size=40, fill=Colors.TEXT,
                 hover_fill="#F0F0F0", glyph_color=Colors.BLACK,
                 bg=Colors.CARD, command=None):
        super().__init__(
            parent, bg=bg, bd=0, highlightthickness=0,
            cursor="hand2", takefocus=0,
        )
        self._glyph = glyph
        self._size = size
        self._fill = fill
        self._hover_fill = hover_fill
        self._glyph_color = glyph_color
        self._command = command
        self._hovered = False

        self._refresh()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _refresh(self):
        fill = self._hover_fill if self._hovered else self._fill
        self.config(
            image=icons.circle(self._glyph, self._size, fill, self._glyph_color)
        )

    def set_glyph(self, glyph):
        self._glyph = glyph
        self._refresh()

    def _on_enter(self, event):
        self._hovered = True
        self._refresh()

    def _on_leave(self, event):
        self._hovered = False
        self._refresh()

    def _on_release(self, event):
        if self._command and _clicked_inside(self, event):
            self._command()


class PillButton(tk.Label):

    def __init__(self, parent, text, *, command, bg=Colors.CARD,
                 height=32, pad_x=18):
        label_font = font(10, "bold")
        width = tkfont.Font(font=label_font).measure(text) + pad_x * 2

        self._normal = icons.pill(width, height, border=Colors.TEXT_SUBTLE)
        self._hover = icons.pill(width, height, border=Colors.TEXT)
        self._command = command

        super().__init__(
            parent, text=text, image=self._normal, compound="center",
            font=label_font, fg=Colors.TEXT, bg=bg, bd=0,
            highlightthickness=0, cursor="hand2", takefocus=0,
        )

        self.bind("<Enter>", lambda e: self.config(image=self._hover))
        self.bind("<Leave>", lambda e: self.config(image=self._normal))
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_release(self, event):
        if _clicked_inside(self, event):
            self._command()


class SeekBar(tk.Canvas):

    PADDING = 6  # room for the knob at both ends

    def __init__(self, parent, *, bg, maximum=100, value=0, width=100,
                 on_press=None, on_change=None, on_release=None):
        super().__init__(
            parent, width=width, height=16, bg=bg,
            highlightthickness=0, bd=0, cursor="hand2",
        )
        self._maximum = float(maximum)
        self._value = float(value)
        self._hovered = False
        self._dragging = False
        self._on_press = on_press
        self._on_change = on_change
        self._on_release = on_release

        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<ButtonRelease-1>", self._release)

    # --- Public --------------------------------------------------------
    @property
    def value(self):
        return self._value

    def set_range(self, maximum):
        self._maximum = max(float(maximum), 0.001)
        self._draw()

    def set_value(self, value):
        """Move the bar (ignored while the user is dragging it)."""
        if self._dragging:
            return

        self._value = min(max(float(value), 0.0), self._maximum)
        self._draw()

    # --- Drawing -------------------------------------------------------
    def _draw(self):
        self.delete("all")

        width = self.winfo_width()
        if width <= 1:
            width = int(self.cget("width"))

        left = self.PADDING
        right = width - self.PADDING
        middle = int(self.cget("height")) // 2
        active = self._hovered or self._dragging

        fraction = self._value / self._maximum
        x = left + (right - left) * fraction

        self.create_line(
            left, middle, right, middle,
            width=4, fill=Colors.TRACK, capstyle="round",
        )

        if x > left:
            self.create_line(
                left, middle, x, middle, width=4,
                fill=Colors.GREEN if active else Colors.TEXT,
                capstyle="round",
            )

        if active:
            self.create_oval(
                x - 6, middle - 6, x + 6, middle + 6,
                fill=Colors.TEXT, outline="",
            )

    # --- Mouse handling ------------------------------------------------
    def _value_at(self, x):
        span = max(self.winfo_width() - 2 * self.PADDING, 1)
        fraction = min(max((x - self.PADDING) / span, 0.0), 1.0)
        return fraction * self._maximum

    def _on_enter(self, event):
        self._hovered = True
        self._draw()

    def _on_leave(self, event):
        self._hovered = False
        self._draw()

    def _press(self, event):
        self._dragging = True
        self._value = self._value_at(event.x)
        self._draw()

        if self._on_press:
            self._on_press(self._value)
        if self._on_change:
            self._on_change(self._value)

    def _drag(self, event):
        if not self._dragging:
            return

        self._value = self._value_at(event.x)
        self._draw()

        if self._on_change:
            self._on_change(self._value)

    def _release(self, event):
        if not self._dragging:
            return

        self._dragging = False
        self._value = self._value_at(event.x)
        self._draw()

        if self._on_release:
            self._on_release(self._value)