"""DualSolver - About/help page mixin."""

import tkinter as tk
from tkinter import ttk, font as tkfont

from gui import themes
from gui.rounded import RoundedFrame


APP_VERSION = "1.0.0"


class AboutMixin:
    """Mixed into DualSolverApp - full-page About/Help panel."""

    def show_about_page(self) -> None:
        """Replace chat content with a full-page About/Help view."""
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
        version_font = tkfont.Font(family=_ui, size=11, weight="bold")
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
            text="DualSolver Help and About",
            font=title_font,
            bg=p["BG"],
            fg=p["TEXT_BRIGHT"],
        ).pack(side=tk.LEFT, padx=(12, 0))

        tk.Label(
            header_row,
            text=f"Version {APP_VERSION}",
            font=version_font,
            bg=p["STEP_BG"],
            fg=p["ACCENT"],
            padx=10,
            pady=4,
        ).pack(side=tk.RIGHT)

        def _section_card(parent) -> tk.Frame:
            card_rf = RoundedFrame(
                parent,
                bg_color=p["STEP_BG"],
                border_color=p["STEP_BORDER"],
                corner_radius=themes.CORNER_RADIUS,
                border_width=1,
                padding=6,
            )
            card_rf.pack(fill=tk.X, pady=(16, 0))
            card = card_rf.inner
            card.configure(padx=24, pady=18)
            return card

        def _line(parent, text: str, *, font=body_font,
                  fg=p["TEXT_BRIGHT"], pady=(0, 4), mono=False) -> None:
            tk.Label(
                parent,
                text=text,
                font=self._mono if mono else font,
                bg=p["STEP_BG"],
                fg=fg,
                justify=tk.LEFT,
                wraplength=920,
                anchor="w",
            ).pack(anchor="w", fill=tk.X, pady=pady)

        intro = _section_card(center)

        tk.Label(
            intro,
            text="What This App Is",
            font=section_font,
            bg=p["STEP_BG"],
            fg=p["ACCENT"],
        ).pack(anchor="w", pady=(0, 8))

        _line(
            intro,
            (
                "DualSolver is a step-by-step solver for linear equations and "
                "systems, designed for symbolic and numerical computation learning."
            ),
        )
        _line(
            intro,
            (
                "Course context: Numeric and Symbolic Computation (COSC 110), "
                "Cavite State University - Imus."
            ),
            font=small_font,
            fg=p["TEXT_DIM"],
            pady=(6, 0),
        )
        _line(
            intro,
            "Standard output flow: GIVEN -> METHOD -> STEPS -> FINAL ANSWER -> VERIFICATION -> SUMMARY",
            font=small_font,
            fg=p["TEXT_DIM"],
            pady=(6, 0),
        )

        how = _section_card(center)

        tk.Label(
            how,
            text="Quick Start",
            font=section_font,
            bg=p["STEP_BG"],
            fg=p["ACCENT"],
        ).pack(anchor="w", pady=(0, 8))

        steps = [
            "1. Enter a linear equation or a system in the input bar.",
            "2. Press Solve (or Enter) and choose a solve mode.",
            "3. Read the generated trail cards in order.",
            "4. Expand Graph and Analysis when available.",
            "5. Export using Copy to Clipboard or Save as PDF.",
            "6. Use New Chat to clear the current conversation.",
        ]
        for step in steps:
            _line(how, step)

        _line(
            how,
            "Shortcuts: Enter to solve, Escape to close Settings/About/Sidebar.",
            font=small_font,
            fg=p["TEXT_DIM"],
            pady=(6, 0),
        )

        modes = _section_card(center)

        tk.Label(
            modes,
            text="Solve Modes",
            font=section_font,
            bg=p["STEP_BG"],
            fg=p["ACCENT"],
        ).pack(anchor="w", pady=(0, 8))

        _line(modes, "- Symbolic (SymPy): exact values, fractions, and symbolic expressions.")
        _line(modes, "- Numerical (NumPy): decimal approximations for linear equations.")
        _line(modes, "- Substitution: checks whether provided values satisfy the equation.")

        features = _section_card(center)

        tk.Label(
            features,
            text="Key Features",
            font=section_font,
            bg=p["STEP_BG"],
            fg=p["ACCENT"],
        ).pack(anchor="w", pady=(0, 8))

        feature_lines = [
            "- Step-by-step solver trail with explanations.",
            "- Verification section and validation status.",
            "- Graph and case analysis panel for supported cases.",
            "- Sidebar history with pin, archive, and delete actions.",
            "- Settings for animation speed and auto-expand behavior.",
            "- Symbol pad for quick equation typing.",
            "- Export trail to clipboard text or PDF.",
        ]
        for line in feature_lines:
            _line(features, line)

        examples = _section_card(center)

        tk.Label(
            examples,
            text="Input Examples",
            font=section_font,
            bg=p["STEP_BG"],
            fg=p["ACCENT"],
        ).pack(anchor="w", pady=(0, 8))

        _line(examples, "Single variable: 3x + 2 = 7", mono=True)
        _line(examples, "Two variables: 2x + 4y = 1", mono=True)
        _line(examples, "System: x + y = 10, x - y = 2", mono=True)
        _line(examples, "Substitution values: x = 3, y = 4", mono=True)
        _line(
            examples,
            "Use comma or semicolon to separate system equations.",
            font=small_font,
            fg=p["TEXT_DIM"],
            pady=(6, 0),
        )

        creators = _section_card(center)

        tk.Label(
            creators,
            text="Creators",
            font=section_font,
            bg=p["STEP_BG"],
            fg=p["ACCENT"],
        ).pack(anchor="w", pady=(0, 8))

        _line(creators, "DualSolver Version: " + APP_VERSION, font=small_font,
              fg=p["TEXT_DIM"], pady=(0, 8))

        for name in [
            "Acal, Lance Adrian",
            "Garcia, Jesly Dinsen",
            "Moreno, Ryel Austin",
        ]:
            _line(creators, name, pady=(0, 3))

        _line(
            creators,
            "Project focus: Symbolic and Numerical Computation to solve linear equations step by step.",
            font=small_font,
            fg=p["TEXT_DIM"],
            pady=(6, 0),
        )

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
