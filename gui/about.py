"""DualSolver - About/help page mixin."""

import os

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
        title_font   = tkfont.Font(family=_ui, size=22, weight="bold")
        version_font = tkfont.Font(family=_ui, size=11, weight="bold")
        section_font = tkfont.Font(family=_ui, size=15, weight="bold")
        body_font    = tkfont.Font(family=_ui, size=13)
        small_font   = tkfont.Font(family=_ui, size=12)
        tab_font     = tkfont.Font(family=_ui, size=13, weight="bold")

        center = tk.Frame(about_inner, bg=p["BG"])
        center.pack(anchor="n", pady=(40, 40), padx=60, fill=tk.X)

        # ── Header ───────────────────────────────────────────────────────────────
        header_row = tk.Frame(center, bg=p["BG"])
        header_row.pack(fill=tk.X, pady=(0, 20))

        back_icon = getattr(self, "_back_icon_photo", None)
        if back_icon is None:
            try:
                icon_path = os.path.normpath(
                    os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "..",
                        "assets",
                        "back.png",
                    )
                )
                if os.path.exists(icon_path):
                    back_icon = tk.PhotoImage(file=icon_path)
                    target_px = 22
                    scale = max(1, int(max(
                        back_icon.width() / target_px,
                        back_icon.height() / target_px,
                    )))
                    if scale > 1:
                        back_icon = back_icon.subsample(scale, scale)
                    self._back_icon_photo = back_icon
            except Exception:
                back_icon = None

        if back_icon is not None:
            tk.Button(
                header_row,
                image=back_icon,
                bg=p["BG"],
                activebackground=p["BG"],
                bd=0,
                highlightthickness=0,
                padx=2,
                pady=2,
                cursor="hand2",
                command=self.close_about_page,
            ).pack(side=tk.LEFT)
        else:
            back_font = tkfont.Font(family=_ui, size=18)
            tk.Button(
                header_row,
                text="←",
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
            text="Help and About",
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

        # ── Tab switcher ─────────────────────────────────────────────────────────
        tab_row = tk.Frame(center, bg=p["BG"])
        tab_row.pack(fill=tk.X, pady=(0, 4))

        # Two swappable content frames inside a common container.
        content_container = tk.Frame(center, bg=p["BG"])
        content_container.pack(fill=tk.X)

        guide_content = tk.Frame(content_container, bg=p["BG"])
        about_content = tk.Frame(content_container, bg=p["BG"])

        # ── Shared helpers ───────────────────────────────────────────────────────
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

        def _switch_tab(name: str) -> None:
            if name == "guide":
                about_content.pack_forget()
                guide_content.pack(fill=tk.X)
                guide_btn.configure(bg=p["ACCENT"], fg=p["BG"],
                                    activebackground=p["ACCENT"], activeforeground=p["BG"])
                about_btn.configure(bg=p["STEP_BG"], fg=p["TEXT_DIM"],
                                    activebackground=p["STEP_BG"], activeforeground=p["TEXT_BRIGHT"])
            else:
                guide_content.pack_forget()
                about_content.pack(fill=tk.X)
                about_btn.configure(bg=p["ACCENT"], fg=p["BG"],
                                    activebackground=p["ACCENT"], activeforeground=p["BG"])
                guide_btn.configure(bg=p["STEP_BG"], fg=p["TEXT_DIM"],
                                    activebackground=p["STEP_BG"], activeforeground=p["TEXT_BRIGHT"])
            about_canvas.after(50, _update_about_scroll)

        guide_btn = tk.Button(
            tab_row,
            text="User Guide",
            font=tab_font,
            bg=p["ACCENT"],
            fg=p["BG"],
            activebackground=p["ACCENT"],
            activeforeground=p["BG"],
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=lambda: _switch_tab("guide"),
        )
        guide_btn.pack(side=tk.LEFT, padx=(0, 6))

        about_btn = tk.Button(
            tab_row,
            text="About",
            font=tab_font,
            bg=p["STEP_BG"],
            fg=p["TEXT_DIM"],
            activebackground=p["STEP_BG"],
            activeforeground=p["TEXT_BRIGHT"],
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            command=lambda: _switch_tab("about"),
        )
        about_btn.pack(side=tk.LEFT)

        # ── USER GUIDE TAB ───────────────────────────────────────────────────────

        # 1. Interface Overview
        overview = _section_card(guide_content)
        tk.Label(overview, text="Interface Overview", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        _line(overview, "The app has four main areas:")
        _line(overview, "  •  Input Bar (bottom center) - type your equation here and press Solve or Enter.")
        _line(overview, "  •  Results Area (center) - shows the step-by-step solve trail as expandable cards.")
        _line(overview, "  •  Sidebar (left, ☰ icon) - open to browse and manage your solve history.")
        _line(overview, "  •  Symbol Pad (keyboard icon near input bar) - insert math symbols with one click.")

        # 2. Entering Equations
        input_guide = _section_card(guide_content)
        tk.Label(input_guide, text="Entering Equations", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        _line(input_guide, "Type your equation into the input bar. Supported formats:")
        _line(input_guide, "  Single variable:     2x + 5 = 11", mono=True)
        _line(input_guide, "  Two variables:       3x - y = 4", mono=True)
        _line(input_guide, "  System of two eqs:   x + y = 10, x - y = 2", mono=True)
        _line(input_guide, "  With parentheses:    2(x + 3) = 14", mono=True)
        _line(input_guide, "  With fractions:      x/2 + 1 = 3", mono=True)
        _line(input_guide, "  Exponents (^ notation):  x^2 + x = 6", mono=True)
        _line(input_guide,
              "Separate two equations in a system with a comma (,) or semicolon (;).",
              font=small_font, fg=p["TEXT_DIM"], pady=(8, 2))
        _line(input_guide,
              "Unicode minus signs, full-width digits, and smart quotes are accepted - "
              "the solver normalizes them automatically before parsing.",
              font=small_font, fg=p["TEXT_DIM"], pady=(0, 2))
        _line(input_guide,
              "π and √ are also accepted and converted to pi and sqrt internally.",
              font=small_font, fg=p["TEXT_DIM"], pady=(0, 0))

        # 3. Choosing a Solve Mode
        modes_guide = _section_card(guide_content)
        tk.Label(modes_guide, text="Choosing a Solve Mode", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        _line(modes_guide, "After pressing Solve (or Enter), a popup asks which mode to use:")
        _line(modes_guide, "  Symbolic - Exact answers as fractions or symbolic expressions (powered by SymPy).")
        _line(modes_guide, "                Best for learning: shows every algebraic step with property names.")
        _line(modes_guide, "  Numerical - Decimal approximations (powered by NumPy).")
        _line(modes_guide, "                Best when a quick numeric result is all you need.")
        _line(modes_guide, "  Substitution - Checks whether specific values satisfy the equation.")
        _line(modes_guide, "                After selecting this mode a Values field appears in the input area.")
        _line(modes_guide,
              "For most study use-cases, start with Symbolic - it shows the most detail.",
              font=small_font, fg=p["TEXT_DIM"], pady=(8, 0))

        # 4. Reading the Results
        results_guide = _section_card(guide_content)
        tk.Label(results_guide, text="Reading the Results", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        _line(results_guide, "Each solve produces a trail of cards displayed in order:")
        entries = [
            ("GIVEN",        "The equation as the solver parsed it (after normalization)."),
            ("METHOD",       "The algorithm used and key parameters (variable count, equation type)."),
            ("STEPS",        "Numbered derivation steps. Each step names the algebraic rule applied\n"
                             "                  (e.g. Subtraction Property of Equality, Distributive Property)."),
            ("FINAL ANSWER", "The solution, or a special message if no unique solution exists\n"
                             "                  (tautology, contradiction, or non-linear notice)."),
            ("VERIFICATION", "The answer is substituted back into the original equation to confirm it."),
            ("SUMMARY",      "Runtime, total step count, validation status (PASS / FAIL), and timestamp."),
        ]
        for label, desc in entries:
            row_f = tk.Frame(results_guide, bg=p["STEP_BG"])
            row_f.pack(anchor="w", fill=tk.X, pady=(0, 4))
            tk.Label(row_f, text=f"{label:<16}", font=self._mono, bg=p["STEP_BG"],
                     fg=p["ACCENT"]).pack(side=tk.LEFT, anchor="nw")
            tk.Label(row_f, text=desc, font=body_font, bg=p["STEP_BG"],
                     fg=p["TEXT_BRIGHT"], justify=tk.LEFT, wraplength=720,
                     anchor="nw").pack(side=tk.LEFT, anchor="nw")
        _line(results_guide,
              "Click a card header to expand or collapse it. A GRAPH & ANALYSIS card appears below "
              "the summary for single-variable linear equations.",
              font=small_font, fg=p["TEXT_DIM"], pady=(8, 0))

        # 5. Substitution Mode
        subst_guide = _section_card(guide_content)
        tk.Label(subst_guide, text="Using Substitution Mode", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        _line(subst_guide,
              "Substitution mode lets you check whether a set of specific values satisfies an equation.")
        _line(subst_guide, "How to use it:")
        _line(subst_guide, "  1.  Enter the equation in the input bar, e.g.   2x + y = 8")
        _line(subst_guide, "  2.  Press Solve and select Substitution from the mode popup.")
        _line(subst_guide, "  3.  A Values field appears - enter the values to test:")
        _line(subst_guide, "          x = 3, y = 2     or     x = 5", mono=True)
        _line(subst_guide, "  4.  Press Solve again. The result will be True, False, or Indeterminate.")
        _line(subst_guide,
              "Indeterminate means one or more variables were left unspecified, so the result "
              "depends on those free values.",
              font=small_font, fg=p["TEXT_DIM"], pady=(8, 0))

        # 6. Symbol Pad
        sympad_guide = _section_card(guide_content)
        tk.Label(sympad_guide, text="Using the Symbol Pad", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        _line(sympad_guide,
              "The symbol pad inserts math characters directly into the input bar at the cursor position. "
              "Open it by clicking the keyboard icon near the input bar.")
        _line(sympad_guide, "Available symbols include: ÷  ×  √  π  ²  ³  and common operators.")
        _line(sympad_guide,
              "Both the symbol form (√, π) and the text form (sqrt, pi) are accepted by the solver.",
              font=small_font, fg=p["TEXT_DIM"], pady=(6, 0))

        # 7. Sidebar & History
        sidebar_guide = _section_card(guide_content)
        tk.Label(sidebar_guide, text="Sidebar and History", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        _line(sidebar_guide,
              "Every solve is automatically saved. Open the sidebar with the ☰ icon at the top-left.")
        _line(sidebar_guide, "From the sidebar you can:")
        _line(sidebar_guide, "  •  Click any entry to reload that solve in the main results area.")
        _line(sidebar_guide, "  •  Pin important solves to keep them at the top of the list.")
        _line(sidebar_guide, "  •  Archive solves you want to keep but hide from the main list.")
        _line(sidebar_guide, "  •  Delete entries you no longer need.")
        _line(sidebar_guide, "  •  Use the search bar at the top of the sidebar to filter by equation text.")
        _line(sidebar_guide,
              "History is capped at 200 entries and persists between sessions.",
              font=small_font, fg=p["TEXT_DIM"], pady=(6, 0))

        # 8. Exporting Results
        export_guide = _section_card(guide_content)
        tk.Label(export_guide, text="Exporting Results", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        _line(export_guide, "After a solve completes, export buttons appear below the trail:")
        _line(export_guide,
              "  Copy to Clipboard - copies the full trail as plain text, ready to paste anywhere.")
        _line(export_guide,
              "  Export PDF        - saves a formatted PDF to a location you choose.")
        _line(export_guide,
              "  Export HTML       - saves an HTML file that can be opened in any web browser.")
        _line(export_guide,
              "All exports include every section: equation, method, steps, answer, verification, and summary.",
              font=small_font, fg=p["TEXT_DIM"], pady=(6, 0))

        # 9. Settings
        settings_guide = _section_card(guide_content)
        tk.Label(settings_guide, text="Settings", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        _line(settings_guide, "Open Settings from the sidebar menu or the gear icon.")
        settings_items = [
            ("Theme",           "Switch between Light and Dark mode."),
            ("Animation Speed", "Controls how fast the step cards animate in (Slow / Normal / Fast / Off)."),
            ("Auto-Expand",     "When on, all result cards open automatically after solving."),
        ]
        for label, desc in settings_items:
            row_f = tk.Frame(settings_guide, bg=p["STEP_BG"])
            row_f.pack(anchor="w", fill=tk.X, pady=(0, 4))
            tk.Label(row_f, text=f"  {label:<20}", font=body_font, bg=p["STEP_BG"],
                     fg=p["ACCENT"]).pack(side=tk.LEFT, anchor="nw")
            tk.Label(row_f, text=desc, font=body_font, bg=p["STEP_BG"],
                     fg=p["TEXT_BRIGHT"], justify=tk.LEFT, wraplength=680,
                     anchor="nw").pack(side=tk.LEFT, anchor="nw")
        _line(settings_guide, "Settings are saved between sessions.",
              font=small_font, fg=p["TEXT_DIM"], pady=(6, 0))

        # 10. Keyboard Shortcuts
        shortcuts_guide = _section_card(guide_content)
        tk.Label(shortcuts_guide, text="Keyboard Shortcuts", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        for key, desc in [
            ("Enter",  "Submit / Solve the equation currently in the input bar."),
            ("Escape", "Close the active panel (Settings, Help & About, or Sidebar)."),
        ]:
            row_f = tk.Frame(shortcuts_guide, bg=p["STEP_BG"])
            row_f.pack(anchor="w", fill=tk.X, pady=(0, 6))
            tk.Label(row_f, text=key, font=self._mono, bg=p["STEP_BG"],
                     fg=p["ACCENT"], width=10, anchor="w").pack(side=tk.LEFT)
            tk.Label(row_f, text=desc, font=body_font, bg=p["STEP_BG"],
                     fg=p["TEXT_BRIGHT"], anchor="w").pack(side=tk.LEFT)

        # ── ABOUT TAB ────────────────────────────────────────────────────────────

        intro = _section_card(about_content)
        tk.Label(intro, text="What This App Is", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        _line(intro, (
            "DualSolver is a step-by-step solver for linear equations and "
            "systems, designed for symbolic and numerical computation learning."
        ))
        _line(intro, (
            "Course context: Numeric and Symbolic Computation (COSC 110), "
            "Cavite State University – Imus."
        ), font=small_font, fg=p["TEXT_DIM"], pady=(6, 0))
        _line(intro,
              "Standard output flow: GIVEN → METHOD → STEPS → FINAL ANSWER → VERIFICATION → SUMMARY",
              font=small_font, fg=p["TEXT_DIM"], pady=(4, 0))

        tech = _section_card(about_content)
        tk.Label(tech, text="Technology", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        _line(tech, "  •  Python 3 - core language.")
        _line(tech, "  •  Tkinter - native desktop GUI, no browser required.")
        _line(tech, "  •  SymPy - symbolic math engine for exact solutions.")
        _line(tech, "  •  NumPy - numerical engine for decimal approximations.")
        _line(tech, "  •  Matplotlib - equation graph rendering.")
        _line(tech, "Fully offline - no internet connection or accounts required.",
              font=small_font, fg=p["TEXT_DIM"], pady=(6, 0))

        creators = _section_card(about_content)
        tk.Label(creators, text="Creators", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))
        _line(creators, "DualSolver Version: " + APP_VERSION,
              font=small_font, fg=p["TEXT_DIM"], pady=(0, 8))
        for name in [
            "Acal, Lance Adrian",
            "Garcia, Jesly Dinsen",
            "Moreno, Ryel Austin",
        ]:
            _line(creators, name, pady=(0, 3))
        _line(creators,
              "Project focus: Symbolic and Numerical Computation to solve linear equations step by step.",
              font=small_font, fg=p["TEXT_DIM"], pady=(6, 0))

        # Show User Guide tab by default.
        guide_content.pack(fill=tk.X)

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
        self._entry.focus_set()
