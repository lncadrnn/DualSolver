"""
DualSolver - About page mixin.

Provides a full-page About view that explains what the app does,
how to use it, and who built it.
"""

import tkinter as tk
from tkinter import ttk, font as tkfont

from gui import themes
from gui.rounded import RoundedFrame


class AboutMixin:
    """Mixed into DualSolverApp - full-page About panel."""

    def show_about_page(self) -> None:
        """Replace chat content with a full-page About view."""
        if getattr(self, "_settings_visible", False):
            self.close_settings_page()

        if hasattr(self, "_about_frame") and self._about_frame.winfo_exists():
            self._about_frame.destroy()

        if not self._about_visible:
            self._chat_wrapper.pack_forget()
            self._input_bar.pack_forget()
            self._new_btn.pack_forget()
            if hasattr(self, "_about_btn") and self._about_btn.winfo_exists():
                self._about_btn.pack_forget()
            self._about_visible = True

        p = themes.palette(self._theme)

        self._about_frame = tk.Frame(self._content, bg=p["BG"])
        self._about_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollable inner content.
        about_canvas = tk.Canvas(self._about_frame, bg=p["BG"], highlightthickness=0)
        about_sb = ttk.Scrollbar(
            self._about_frame,
            orient=tk.VERTICAL,
            command=about_canvas.yview,
            style=self._sb_style_name,
        )
        about_inner = tk.Frame(about_canvas, bg=p["BG"])
        about_canvas.create_window((0, 0), window=about_inner, anchor="nw", tags="about_inner")
        about_canvas.configure(yscrollcommand=about_sb.set)

        about_sb.pack(side=tk.RIGHT, fill=tk.Y)
        about_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def _update_about_scroll(_=None):
            about_canvas.configure(scrollregion=about_canvas.bbox("all"))
            about_canvas.update_idletasks()
            content_h = about_inner.winfo_reqheight()
            canvas_h = about_canvas.winfo_height()
            if content_h <= canvas_h:
                about_sb.pack_forget()
            elif not about_sb.winfo_ismapped():
                about_sb.pack(side=tk.RIGHT, fill=tk.Y)

        about_inner.bind("<Configure>", _update_about_scroll)
        about_canvas.bind(
            "<Configure>",
            lambda e: (about_canvas.itemconfig("about_inner", width=e.width),
                       _update_about_scroll()),
        )

        self._about_canvas = about_canvas

        def _about_mousewheel(e):
            if about_canvas.winfo_exists():
                about_canvas.yview_scroll(int(-e.delta / 120), "units")

        self._about_scroll_id = about_canvas.bind_all("<MouseWheel>", _about_mousewheel)

        _ui = getattr(self, "_ui_family", "Segoe UI")
        title_font = tkfont.Font(family=_ui, size=22, weight="bold")
        section_font = tkfont.Font(family=_ui, size=15, weight="bold")
        body_font = tkfont.Font(family=_ui, size=13)
        small_font = tkfont.Font(family=_ui, size=12)

        center = tk.Frame(about_inner, bg=p["BG"])
        center.pack(anchor="n", pady=(40, 40), padx=60, fill=tk.X)

        header_row = tk.Frame(center, bg=p["BG"])
        header_row.pack(fill=tk.X, pady=(0, 20))

        back_font = tkfont.Font(family=_ui, size=18)
        tk.Button(
            header_row,
            text="<-",
            font=back_font,
            bg=p["BG"],
            fg=p["TEXT_DIM"],
            activebackground=p["BG"],
            activeforeground=p["TEXT_BRIGHT"],
            bd=0,
            cursor="hand2",
            command=self.close_about_page,
        ).pack(side=tk.LEFT)

        tk.Label(
            header_row,
            text="About DualSolver",
            font=title_font,
            bg=p["BG"],
            fg=p["TEXT_BRIGHT"],
        ).pack(side=tk.LEFT, padx=(12, 0))

        intro_rf = RoundedFrame(
            center,
            bg_color=p["STEP_BG"],
            border_color=p["STEP_BORDER"],
            corner_radius=themes.CORNER_RADIUS,
            border_width=1,
            padding=6,
        )
        intro_rf.pack(fill=tk.X)
        intro = intro_rf.inner
        intro.configure(padx=24, pady=18)

        tk.Label(
            intro,
            text="What This App Is",
            font=section_font,
            bg=p["STEP_BG"],
            fg=p["ACCENT"],
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            intro,
            text=(
                "DualSolver is a project to solve linear equations step by step "
                "using symbolic and numerical computation."
            ),
            font=body_font,
            bg=p["STEP_BG"],
            fg=p["TEXT_BRIGHT"],
            justify=tk.LEFT,
            wraplength=900,
        ).pack(anchor="w")

        tk.Label(
            intro,
            text=(
                "This project was developed for Numeric and Symbolic Computation "
                "(COSC 110) at Cavite State University - Imus."
            ),
            font=small_font,
            bg=p["STEP_BG"],
            fg=p["TEXT_DIM"],
            justify=tk.LEFT,
            wraplength=900,
        ).pack(anchor="w", pady=(10, 0))

        how_rf = RoundedFrame(
            center,
            bg_color=p["STEP_BG"],
            border_color=p["STEP_BORDER"],
            corner_radius=themes.CORNER_RADIUS,
            border_width=1,
            padding=6,
        )
        how_rf.pack(fill=tk.X, pady=(16, 0))
        how = how_rf.inner
        how.configure(padx=24, pady=18)

        tk.Label(
            how,
            text="How To Use",
            font=section_font,
            bg=p["STEP_BG"],
            fg=p["ACCENT"],
        ).pack(anchor="w", pady=(0, 8))

        steps = [
            "1. Type a linear equation or system in the input bar.",
            "2. Press Solve and choose Symbolic, Numerical, or Substitution mode.",
            "3. Read each solution phase and final answer in the chat panel.",
            "4. Use New Chat to reset and solve another problem.",
        ]
        for step in steps:
            tk.Label(
                how,
                text=step,
                font=body_font,
                bg=p["STEP_BG"],
                fg=p["TEXT_BRIGHT"],
                justify=tk.LEFT,
                wraplength=900,
            ).pack(anchor="w", pady=(0, 4))

        creators_rf = RoundedFrame(
            center,
            bg_color=p["STEP_BG"],
            border_color=p["STEP_BORDER"],
            corner_radius=themes.CORNER_RADIUS,
            border_width=1,
            padding=6,
        )
        creators_rf.pack(fill=tk.X, pady=(16, 0))
        creators = creators_rf.inner
        creators.configure(padx=24, pady=18)

        tk.Label(
            creators,
            text="Creators",
            font=section_font,
            bg=p["STEP_BG"],
            fg=p["ACCENT"],
        ).pack(anchor="w", pady=(0, 8))

        for name in [
            "Acal, Lance Adrian",
            "Garcia, Jesly Dinsen",
            "Moreno, Ryel Austin",
        ]:
            tk.Label(
                creators,
                text=name,
                font=body_font,
                bg=p["STEP_BG"],
                fg=p["TEXT_BRIGHT"],
                justify=tk.LEFT,
            ).pack(anchor="w", pady=(0, 3))

    def close_about_page(self) -> None:
        """Destroy the About page and restore the chat view."""
        if not self._about_visible:
            return

        if hasattr(self, "_about_scroll_id") and hasattr(self, "_about_canvas"):
            try:
                self._about_canvas.unbind_all("<MouseWheel>")
                self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
            except Exception:
                pass

        if hasattr(self, "_about_frame") and self._about_frame.winfo_exists():
            self._about_frame.destroy()

        self._about_visible = False
        self._chat_wrapper.pack(fill=tk.BOTH, expand=True)
        self._input_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self._new_btn.pack(side=tk.RIGHT, padx=(0, 20), pady=16)
        if hasattr(self, "_about_btn") and self._about_btn.winfo_exists():
            self._about_btn.pack(side=tk.RIGHT, padx=(0, 8), pady=16)
        self._entry.focus_set()
