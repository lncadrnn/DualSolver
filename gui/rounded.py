"""
DualSolver — Rounded widget helpers for the solid UI.

Canvas-based widgets that provide rounded corners for frames, buttons,
and input containers within standard Tkinter.
"""

import tkinter as tk
import tkinter.font as tkfont


def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    """Draw a rounded rectangle on *canvas* using a smooth polygon."""
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class RoundedFrame(tk.Canvas):
    """A Canvas that draws a rounded-rectangle background and hosts
    child widgets inside an embedded ``inner`` Frame.

    The optional ``glass`` parameters are retained for backward
    compatibility and simply add an extra inner highlight ring.

    Usage::

        rf = RoundedFrame(parent, bg_color="#101628",
                          border_color="#1e2848", corner_radius=18,
                          glass=True)
        rf.pack(fill=tk.X, padx=20)
        tk.Label(rf.inner, text="Hello").pack()
    """

    def __init__(self, parent, bg_color, corner_radius=18,
                 border_color=None, border_width=1, padding=0,
                 glass=False, glass_highlight=None, **kwargs):
        parent_bg = _widget_bg(parent)
        super().__init__(parent, highlightthickness=0, bd=0,
                         bg=parent_bg, **kwargs)
        self._bg_color = bg_color
        self._border_color = border_color or bg_color
        self._radius = corner_radius
        self._bw = border_width
        self._pad = padding
        # Optional inner highlight ring (legacy option)
        self._glass = glass
        self._glass_hl = glass_highlight

        self.inner = tk.Frame(self, bg=bg_color, bd=0)
        self._win_id = self.create_window(0, 0, window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_inner_resize)
        self.bind("<Configure>", self._redraw)

    def _on_inner_resize(self, event):
        """Auto-size the canvas height to fit inner content."""
        offset = self._bw + self._pad
        needed_h = event.height + 2 * offset
        if abs(self.winfo_height() - needed_h) > 1:
            self.configure(height=needed_h)

    def _redraw(self, event=None):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 4 or h < 4:
            return

        self.delete("bg")
        r = self._radius
        bw = self._bw

        if bw > 0 and self._border_color != self._bg_color:
            draw_rounded_rect(self, 0, 0, w, h, r,
                              fill=self._border_color, outline="", tags="bg")
            # Optional inner highlight ring
            if self._glass and self._glass_hl:
                hl_w = 1  # highlight thickness
                draw_rounded_rect(self, bw, bw, w - bw, h - bw,
                                  max(r - bw, 2),
                                  fill=self._glass_hl, outline="", tags="bg")
                inner_off = bw + hl_w
                draw_rounded_rect(self, inner_off, inner_off,
                                  w - inner_off, h - inner_off,
                                  max(r - inner_off, 2),
                                  fill=self._bg_color, outline="", tags="bg")
            else:
                draw_rounded_rect(self, bw, bw, w - bw, h - bw, max(r - bw, 2),
                                  fill=self._bg_color, outline="", tags="bg")
        else:
            draw_rounded_rect(self, 0, 0, w, h, r,
                              fill=self._bg_color, outline="", tags="bg")

        self.tag_lower("bg")

        offset = bw + self._pad
        inner_w = max(w - 2 * offset, 1)
        self.coords(self._win_id, offset, offset)
        self.itemconfig(self._win_id, width=inner_w)

    def update_colors(self, bg_color=None, border_color=None, parent_bg=None):
        """Update colours (e.g. on theme switch) and redraw."""
        if parent_bg is not None:
            self.configure(bg=parent_bg)
        if bg_color is not None:
            self._bg_color = bg_color
            self.inner.configure(bg=bg_color)
        if border_color is not None:
            self._border_color = border_color
        # Trigger a redraw
        self._redraw()


class RoundedButton(tk.Canvas):
    """A button drawn on a Canvas with rounded corners.

    Supports hover effects, accent outlines, and colour updates
    for theme switching.
    """

    def __init__(self, parent, text="", command=None, font=None,
                 bg="#0096C7", fg="#ffffff", hover_bg="#00B4D8",
                 hover_fg="#ffffff", corner_radius=12,
                 padx=20, pady=8, glow_color=None, **kwargs):
        parent_bg = _widget_bg(parent)
        super().__init__(parent, highlightthickness=0, bd=0,
                         bg=parent_bg, cursor="hand2", **kwargs)

        self._bg_val = bg
        self._fg_val = fg
        self._hover_bg = hover_bg
        self._hover_fg = hover_fg
        self._radius = corner_radius
        self._cmd = command
        self._text = text
        self._font = font
        self._padx = padx
        self._pady = pady
        self._glow = glow_color    # accent outline shown on hover
        self._rect_id = None
        self._glow_id = None       # outer glow ring (drawn on hover)
        self._text_id = None

        # Measure text to set initial canvas size
        f = tkfont.Font(font=self._font) if self._font else tkfont.Font()
        tw = f.measure(self._text)
        th = f.metrics("linespace")
        self.configure(width=tw + 2 * padx, height=th + 2 * pady)

        self.bind("<Button-1>", lambda _: self._cmd() if self._cmd else None)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        w, h = event.width, event.height
        if w < 4 or h < 4:
            return
        self.delete("all")
        # Optional glow ring (hidden initially, shown on hover)
        if self._glow:
            self._glow_id = draw_rounded_rect(
                self, 0, 0, w, h, self._radius,
                fill="", outline=self._glow, width=0, tags="glow",
            )
            self.itemconfig(self._glow_id, state="hidden")
        self._rect_id = draw_rounded_rect(
            self, 1, 1, w - 1, h - 1, self._radius,
            fill=self._bg_val, outline="",
        )
        self._text_id = self.create_text(
            w // 2, h // 2, text=self._text, font=self._font,
            fill=self._fg_val,
        )

    def _on_enter(self, _event):
        if self._glow_id:
            self.itemconfig(self._glow_id, state="normal",
                            outline=self._glow, width=2)
        if self._rect_id:
            self.itemconfig(self._rect_id, fill=self._hover_bg)
        if self._text_id:
            self.itemconfig(self._text_id, fill=self._hover_fg)

    def _on_leave(self, _event):
        if self._glow_id:
            self.itemconfig(self._glow_id, state="hidden")
        if self._rect_id:
            self.itemconfig(self._rect_id, fill=self._bg_val)
        if self._text_id:
            self.itemconfig(self._text_id, fill=self._fg_val)

    def configure_colors(self, bg=None, fg=None, hover_bg=None,
                         hover_fg=None, parent_bg=None):
        if parent_bg is not None:
            self.configure(bg=parent_bg)
        if bg is not None:
            self._bg_val = bg
        if fg is not None:
            self._fg_val = fg
        if hover_bg is not None:
            self._hover_bg = hover_bg
        if hover_fg is not None:
            self._hover_fg = hover_fg
        if self._rect_id:
            self.itemconfig(self._rect_id, fill=self._bg_val)
        if self._text_id:
            self.itemconfig(self._text_id, fill=self._fg_val)

    def set_text(self, text):
        self._text = text
        if self._text_id:
            self.itemconfig(self._text_id, text=text)


def _widget_bg(widget):
    """Safely retrieve a widget's background colour."""
    try:
        return widget.cget("bg")
    except Exception:
        return "#000000"
