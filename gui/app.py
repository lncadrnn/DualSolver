"""
DualSolver — Tkinter GUI (solid dark theme)

A chat-style interface for solving linear equations step-by-step.
Solid-color dark styling with rounded panels and animated
step-by-step solutions.
"""

import os
import tkinter as tk
from tkinter import ttk, font as tkfont
import threading

from solver import solve_linear_equation
from gui.sidebar import Sidebar

# ── Theme data (palettes, mutable colour shortcuts) ────────────────────────
from gui import themes

# ── Mixin classes (each in its own module) ─────────────────────────────────
from gui.animation import AnimationMixin
from gui.widgets import WidgetMixin
from gui.export import ExportMixin
from gui.symbolpad import SymbolPadMixin
from gui.settings import SettingsMixin
from gui.about import AboutMixin
from gui.rounded import RoundedFrame, RoundedButton


class DualSolverApp(
    AnimationMixin,
    WidgetMixin,
    ExportMixin,
    SymbolPadMixin,
    SettingsMixin,
    AboutMixin,
    tk.Tk,
):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("DualSolver — Linear Equation Solver")
        self.geometry("1000x850")
        self.minsize(680, 600)
        self.configure(bg=themes.BG)

        # Keep an explicit flag for compatibility with older UI code paths.
        self._blur_active = False

        # ── Fonts (modern family with fallback) ────────────────────
        _ui = "Segoe UI Variable"
        _mono_family = "Cascadia Code"
        # Verify the modern fonts exist, fall back to classics
        _avail = tkfont.families(self)
        if _ui not in _avail:
            _ui = "Segoe UI"
        if _mono_family not in _avail:
            _mono_family = "Consolas"

        self._default = tkfont.Font(family=_ui, size=14)
        self._bold    = tkfont.Font(family=_ui, size=14, weight="bold")
        self._title   = tkfont.Font(family=_ui, size=22, weight="bold")
        self._mono    = tkfont.Font(family=_mono_family, size=15)
        self._small   = tkfont.Font(family=_ui, size=12)
        self._frac    = tkfont.Font(family=_mono_family, size=13)
        self._frac_sm = tkfont.Font(family=_mono_family, size=11)
        self._ui_family = _ui
        self._mono_family = _mono_family

        self._auto_scroll: bool = True
        self._theme: str = "dark"
        self._graph_panels: list = []
        self._logo_photo = None
        self._show_verification: bool = False
        self._show_graph: bool = True
        self._settings_visible: bool = False
        self._about_visible: bool = False
        self._solve_gen: int = 0

        self._build_ui()
        self._sidebar = Sidebar(self)
        self._sidebar._apply_user_settings()
        self._show_welcome()

        self.bind("<Return>", lambda _: self._on_send())
        self.bind(
            "<Escape>",
            lambda _: self.close_settings_page()
            if self._settings_visible else self.close_about_page()
            if self._about_visible else self._sidebar.close(),
        )

    # ── UI construction ─────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # ── Main content wrapper ─────────────────────────────────────
        self._content = tk.Frame(self, bg=themes.BG)
        self._content.pack(fill=tk.BOTH, expand=True)

        # header
        self._header = tk.Frame(self._content, bg=themes.HEADER_BG, height=72)
        self._header.pack(fill=tk.X)
        self._header.pack_propagate(False)

        self._hamburger_font = tkfont.Font(family=self._ui_family, size=20)
        self._hamburger_btn = tk.Button(
            self._header, text="☰", font=self._hamburger_font,
            bg=themes.HEADER_BG, fg=themes.TEXT_DIM,
            activebackground=themes.HEADER_BG,
            activeforeground=themes.TEXT_BRIGHT,
            bd=0, padx=10, pady=0, cursor="hand2", relief=tk.FLAT,
            command=self._toggle_sidebar,
        )
        self._hamburger_btn.pack(side=tk.LEFT, padx=(14, 0))

        self._header_logo = self._load_header_logo()
        self._header_logo.pack(side=tk.LEFT, padx=(8, 0))

        self._header_title_font = tkfont.Font(family=self._ui_family, size=18, weight="bold")
        self._header_title = tk.Label(
            self._header, text="DualSolver", font=self._header_title_font,
            bg=themes.HEADER_BG, fg=themes.TEXT_BRIGHT,
        )
        self._header_title.pack(side=tk.LEFT, padx=(6, 20))

        self._small_bold = tkfont.Font(family=self._ui_family, size=12, weight="bold")
        self._new_btn = RoundedButton(
            self._header, text="+ New Chat", font=self._small_bold,
            bg=themes.ACCENT, fg="#ffffff",
            hover_bg=themes.ACCENT_HOVER, hover_fg="#ffffff",
            corner_radius=themes.CORNER_RADIUS_BTN,
            padx=18, pady=7,
            command=self._clear_chat,
        )
        self._new_btn.pack(side=tk.RIGHT, padx=(0, 20), pady=16)

        # chat area
        self._chat_wrapper = tk.Frame(self._content, bg=themes.BG)
        self._chat_wrapper.pack(fill=tk.BOTH, expand=True)

        self._sb_style_name = "Themed.Vertical.TScrollbar"
        self._style = ttk.Style()
        self._style.theme_use("default")
        self._update_scrollbar_style()

        self._canvas = tk.Canvas(self._chat_wrapper, bg=themes.BG,
                                 highlightthickness=0)
        self._scrollbar = ttk.Scrollbar(
            self._chat_wrapper, orient=tk.VERTICAL,
            command=self._canvas.yview,
            style=self._sb_style_name,
        )
        self._chat_frame = tk.Frame(self._canvas, bg=themes.BG)

        self._chat_frame.bind("<Configure>",
                              lambda _: self._update_scroll_region())
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._chat_frame, anchor="nw",
        )
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # input bar
        self._input_bar = tk.Frame(self._content, bg=themes.BG_DARKER, pady=14)
        self._input_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self._input_rounded = RoundedFrame(
            self._input_bar,
            bg_color=themes.INPUT_BG,
            border_color=themes.INPUT_BORDER,
            corner_radius=themes.CORNER_RADIUS,
            border_width=2,
            padding=2,
        )
        self._input_rounded.pack(fill=tk.X, padx=20)
        self._input_inner = self._input_rounded.inner

        self._entry_var = tk.StringVar()
        self._entry = tk.Entry(
            self._input_inner, font=self._mono, bg=themes.INPUT_BG,
            fg=themes.TEXT_BRIGHT, insertbackground=themes.TEXT_BRIGHT,
            bd=0, relief=tk.FLAT,
            disabledbackground=themes.INPUT_BG,
            disabledforeground=themes.TEXT_DIM,
            textvariable=self._entry_var,
        )
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True,
                         padx=(16, 6), pady=12)
        self._entry.focus_set()

        # Clear-input (trash) button — visible only when text is present
        self._clear_input_font = tkfont.Font(family=self._ui_family, size=14)
        self._clear_input_btn = tk.Button(
            self._input_inner, text="🗑", font=self._clear_input_font,
            bg=themes.INPUT_BG, fg=themes.ERROR,
            activebackground=themes.INPUT_BG,
            activeforeground="#ff8a80",
            bd=0, padx=4, pady=4, cursor="hand2", relief=tk.FLAT,
            command=self._clear_input_field,
        )
        # Start hidden; show/hide via trace
        self._entry_var.trace_add("write", self._toggle_clear_btn)

        # Solve / Stop buttons
        self._action_frame = tk.Frame(self._input_inner, bg=themes.INPUT_BG)
        self._action_frame.pack(side=tk.RIGHT, padx=(0, 8), pady=6)
        self._action_frame.pack_propagate(False)
        self.after(50, self._lock_action_frame_size)

        self._send_btn = RoundedButton(
            self._action_frame, text="Solve ➤", font=self._bold,
            bg=themes.ACCENT, fg=themes.TEXT_BRIGHT,
            hover_bg=themes.ACCENT_HOVER, hover_fg=themes.TEXT_BRIGHT,
            corner_radius=themes.CORNER_RADIUS_BTN,
            padx=18, pady=6,
            command=self._on_send,
        )
        self._send_btn.pack(fill=tk.BOTH, expand=True)

        self._stop_btn = tk.Button(
            self._action_frame, text="⏹", font=self._bold,
            bg="#2a0e14", fg=themes.ERROR,
            activebackground="#3a1420", activeforeground="#ff8a80",
            bd=0, padx=18, pady=6, cursor="hand2", relief=tk.FLAT,
            command=self._stop_solving,
        )

        # Symbol-pad toggle button
        self._sympad_font = tkfont.Font(family=self._ui_family, size=16)
        self._sympad_btn = tk.Button(
            self._input_inner, text="\u2328", font=self._sympad_font,
            bg=themes.INPUT_BG, fg=themes.TEXT_DIM,
            activebackground=themes.INPUT_BG,
            activeforeground=themes.TEXT_BRIGHT,
            bd=0, padx=8, pady=4, cursor="hand2", relief=tk.FLAT,
            command=self._toggle_symbol_pad,
        )
        self._sympad_btn.pack(side=tk.RIGHT, padx=(0, 2), pady=6)
        self._symbol_pad_win: tk.Toplevel | None = None

    def _lock_action_frame_size(self) -> None:
        """Freeze the action frame to the Solve button's rendered size."""
        self._action_frame.update_idletasks()
        w = self._send_btn.winfo_reqwidth()
        h = self._send_btn.winfo_reqheight()
        self._action_frame.configure(width=w, height=h)

    # ── Input field clear button ────────────────────────────────────────

    def _clear_input_field(self) -> None:
        """Clear the input entry and refocus it."""
        self._entry.delete(0, tk.END)
        self._entry.focus_set()

    def _toggle_clear_btn(self, *_args) -> None:
        """Show the trash button when there is text; hide when empty."""
        if self._entry_var.get().strip():
            if not self._clear_input_btn.winfo_ismapped():
                self._clear_input_btn.pack(side=tk.RIGHT, padx=(0, 2), pady=6)
                # Re-pack sympad so trash sits between entry and sympad
                self._sympad_btn.pack_forget()
                self._clear_input_btn.pack_forget()
                self._sympad_btn.pack(side=tk.RIGHT, padx=(0, 2), pady=6)
                self._clear_input_btn.pack(side=tk.RIGHT, padx=(0, 2), pady=6)
        else:
            self._clear_input_btn.pack_forget()

    # ── Canvas / scroll helpers ─────────────────────────────────────────

    def _on_canvas_resize(self, event: tk.Event) -> None:
        self._canvas.itemconfig(self._canvas_window, width=event.width)
        self._update_scroll_region()

    def _update_scroll_region(self) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._canvas.update_idletasks()
        content_h = self._chat_frame.winfo_reqheight()
        canvas_h = self._canvas.winfo_height()
        if content_h <= canvas_h:
            self._scrollbar.pack_forget()
            self._canvas.yview_moveto(0.0)
            self._scroll_enabled = False
        else:
            if not self._scrollbar.winfo_ismapped():
                self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self._scroll_enabled = True

    def _on_mousewheel(self, event: tk.Event) -> None:
        if getattr(self, '_scroll_enabled', False):
            self._canvas.yview_scroll(int(-event.delta / 120), "units")
            try:
                _, bottom = self._canvas.yview()
                self._auto_scroll = bottom >= 0.99
            except Exception:
                pass

    def _scroll_to_bottom(self) -> None:
        if getattr(self, '_instant_rendering', False):
            return
        if not self._auto_scroll:
            return
        self._canvas.update_idletasks()
        self._canvas.yview_moveto(1.0)

    # ── Theme ────────────────────────────────────────────────────────────

    def _update_scrollbar_style(self) -> None:
        p = themes.palette(self._theme)
        bg  = p["BG"]
        sbg = p["SCROLLBAR_BG"]
        sac = p["SCROLLBAR_ACT"]
        sar = p["SCROLLBAR_ARR"]
        self._style.configure(self._sb_style_name,
                              background=sbg, troughcolor=bg,
                              bordercolor=bg, arrowcolor=sar,
                              relief=tk.FLAT, borderwidth=0)
        self._style.map(self._sb_style_name,
                        background=[("active", sac), ("!active", sbg)],
                        arrowcolor=[("active", "#cccccc"), ("!active", sar)])
        self._style.layout(self._sb_style_name, [
            ("Vertical.Scrollbar.trough", {
                "sticky": "ns",
                "children": [
                    ("Vertical.Scrollbar.thumb", {"expand": 1, "sticky": "nswe"})
                ]
            })
        ])

    def _load_header_logo(self):
        try:
            from PIL import Image, ImageTk
            base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "assets")
            fname = "darkmode-logo.png"
            path = os.path.normpath(os.path.join(base, fname))
            if not os.path.exists(path):
                raise FileNotFoundError(path)
            img = Image.open(path)
            h = 48
            w = int(h * img.width / img.height)
            img = img.resize((w, h), Image.Resampling.LANCZOS)
            self._logo_photo = ImageTk.PhotoImage(img)
            return tk.Label(self._header, image=self._logo_photo,
                            bg=themes.HEADER_BG)
        except Exception as e:
            print(f"Could not load logo: {e}")
            return tk.Label(self._header, text="DualSolver", font=self._title,
                            bg=themes.HEADER_BG, fg=themes.TEXT_BRIGHT)

    def _toggle_sidebar(self) -> None:
        self._sidebar.toggle()



    # ── Welcome screen ──────────────────────────────────────────────────

    def _show_welcome(self) -> None:
        self._welcome_frame = tk.Frame(self._chat_frame, bg=themes.BG)
        self._welcome_frame.pack(fill=tk.BOTH, expand=True, pady=(100, 50))

        tk.Label(
            self._welcome_frame, text="Welcome to DualSolver",
            font=self._title, bg=themes.BG, fg=themes.TEXT_BRIGHT,
        ).pack(pady=(8, 2))
        tk.Label(
            self._welcome_frame,
            text="Type a linear equation or system below and press Solve.",
            font=self._default, bg=themes.BG, fg=themes.TEXT_DIM,
        ).pack(pady=(0, 4))
        tk.Label(
            self._welcome_frame,
            text="Supports one or more variables  •  Separate systems with commas",
            font=self._small, bg=themes.BG, fg=themes.TEXT_DIM,
        ).pack(pady=(0, 20))

        tk.Label(
            self._welcome_frame, text="Try an example:",
            font=self._bold, bg=themes.BG, fg=themes.TEXT_DIM,
        ).pack(pady=(0, 6))

        examples = ["3x + 2 = 7", "x + π = 10"]
        for eq in examples:
            btn = RoundedButton(
                self._welcome_frame, text=eq, font=self._mono,
                bg=themes.STEP_BG, fg=themes.ACCENT,
                hover_bg=themes.ACCENT, hover_fg="#ffffff",
                corner_radius=themes.CORNER_RADIUS_SM,
                padx=24, pady=10,
                command=lambda e=eq: self._use_example(e),
            )
            btn.pack(pady=4)

    def _use_example(self, equation: str) -> None:
        """Fill the input with an example, then ask how to solve it."""
        self._entry.delete(0, tk.END)
        self._entry.insert(0, equation)
        self._show_solve_mode_modal(equation)

    # ── Solve-mode modal ────────────────────────────────────────────────

    def _show_solve_mode_modal(self, equation: str) -> None:
        """Show a centred modal asking the user to pick symbolic or numerical."""
        p = themes.palette(self._theme)

        # Backdrop (dim overlay)
        backdrop = tk.Frame(self, bg="#000000")
        backdrop.place(relx=0, rely=0, relwidth=1, relheight=1)
        backdrop.configure(bg="#050810")
        backdrop.lift()

        # Modal card with solid background + accent border
        modal = tk.Frame(self, bg=p["STEP_BG"], padx=0, pady=0,
                         highlightbackground=p["ACCENT"],
                         highlightthickness=2, bd=0)
        modal.place(relx=0.5, rely=0.5, anchor="center")
        modal.lift()

        inner = tk.Frame(modal, bg=p["STEP_BG"], padx=36, pady=28)
        inner.pack()

        title_font = tkfont.Font(family=self._ui_family, size=18, weight="bold")
        label_font = tkfont.Font(family=self._ui_family, size=13)
        small_font = tkfont.Font(family=self._ui_family, size=11)
        btn_font   = tkfont.Font(family=self._ui_family, size=14, weight="bold")

        tk.Label(inner, text="How do you want this solved?",
                 font=title_font, bg=p["STEP_BG"],
                 fg=p["TEXT_BRIGHT"]).pack(pady=(0, 4))

        eq_display = equation.replace('pi', 'π')
        tk.Label(inner, text=eq_display, font=self._mono,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(pady=(0, 16))

        def _pick(mode):
            backdrop.destroy()
            modal.destroy()
            self._solve_with_mode(equation, mode)

        def _pick_substitution():
            """Switch modal to show the values input for substitution."""
            # Clear existing inner content
            for child in inner.winfo_children():
                child.destroy()

            inner.configure(padx=44, pady=28)

            # Enforce a minimum width for the substitution view
            spacer = tk.Frame(inner, bg=p["STEP_BG"], height=0, width=440)
            spacer.pack(fill=tk.X)
            spacer.pack_propagate(False)

            tk.Label(inner, text="Substitution Mode",
                     font=title_font, bg=p["STEP_BG"],
                     fg=p["TEXT_BRIGHT"]).pack(pady=(0, 4))

            # Show equation
            tk.Label(inner, text="Equation:", font=small_font,
                     bg=p["STEP_BG"], fg=p["TEXT_DIM"],
                     anchor="w").pack(fill=tk.X, pady=(8, 2))
            eq_display2 = equation.replace('pi', 'π')
            tk.Label(inner, text=eq_display2, font=self._mono,
                     bg=p["BG_DARKER"], fg=p["ACCENT"],
                     padx=12, pady=8, anchor="w",
                     relief=tk.FLAT).pack(fill=tk.X, pady=(0, 12))

            # Values input
            tk.Label(inner, text="Enter variable values:",
                     font=small_font, bg=p["STEP_BG"],
                     fg=p["TEXT_DIM"], anchor="w").pack(fill=tk.X, pady=(0, 2))
            tk.Label(inner, text="e.g.  x = 3   or   x = 3, y = 4",
                     font=tkfont.Font(family=self._ui_family, size=10),
                     bg=p["STEP_BG"], fg=p["TEXT_DIM"],
                     anchor="w").pack(fill=tk.X, pady=(0, 6))

            val_entry_frame = tk.Frame(inner, bg=p["INPUT_BG"],
                                        highlightbackground=p["ACCENT"],
                                        highlightthickness=2, bd=0)
            val_entry_frame.pack(fill=tk.X, pady=(0, 6))

            val_var = tk.StringVar()
            val_entry = tk.Entry(
                val_entry_frame, font=self._mono, bg=p["INPUT_BG"],
                fg=p["TEXT_BRIGHT"], insertbackground=p["TEXT_BRIGHT"],
                bd=0, relief=tk.FLAT, textvariable=val_var,
            )
            val_entry.pack(fill=tk.X, padx=10, pady=8)
            val_entry.focus_set()

            # Symbolic / Numerical toggle
            toggle_frame = tk.Frame(inner, bg=p["STEP_BG"])
            toggle_frame.pack(fill=tk.X, pady=(6, 4))
            tk.Label(toggle_frame, text="Compute as:", font=small_font,
                     bg=p["STEP_BG"], fg=p["TEXT_DIM"]
                     ).pack(side=tk.LEFT, padx=(0, 8))

            sub_compute_mode = tk.StringVar(value="symbolic")
            toggle_btn_font = tkfont.Font(family=self._ui_family, size=11,
                                          weight="bold")

            sym_toggle_border = tk.Frame(toggle_frame, bg=p["STEP_BG"],
                                         padx=1, pady=1, bd=0)
            sym_toggle_border.pack(side=tk.LEFT, padx=(0, 4))
            sym_toggle = tk.Button(sym_toggle_border, text="📐 Symbolic",
                                   font=toggle_btn_font,
                                   bg=p["ACCENT"], fg="#ffffff",
                                   activebackground=p["ACCENT_HOVER"],
                                   activeforeground="#ffffff",
                                   bd=0, padx=12, pady=4, cursor="hand2",
                                   relief=tk.FLAT,
                                   highlightthickness=0)
            sym_toggle.pack()

            num_toggle_border = tk.Frame(toggle_frame, bg=p["STEP_BORDER"],
                                         padx=1, pady=1, bd=0)
            num_toggle_border.pack(side=tk.LEFT)
            num_toggle = tk.Button(num_toggle_border, text="🔢 Numerical",
                                   font=toggle_btn_font,
                                   bg=p["STEP_BG"], fg=p["TEXT_DIM"],
                                   activebackground=p["STEP_BG"],
                                   activeforeground=p["TEXT_BRIGHT"],
                                   bd=0, padx=12, pady=4, cursor="hand2",
                                   relief=tk.FLAT,
                                   highlightthickness=0)
            num_toggle.pack()

            def _set_compute(mode_val):
                sub_compute_mode.set(mode_val)
                if mode_val == "symbolic":
                    sym_toggle_border.configure(bg=p["STEP_BG"])
                    num_toggle_border.configure(bg=p["STEP_BORDER"])
                    sym_toggle.configure(bg=p["ACCENT"], fg="#ffffff",
                                         activebackground=p["ACCENT_HOVER"],
                                         activeforeground="#ffffff")
                    num_toggle.configure(bg=p["STEP_BG"], fg=p["TEXT_DIM"],
                                         activebackground=p["STEP_BG"],
                                         activeforeground=p["TEXT_BRIGHT"])
                else:
                    num_toggle_border.configure(bg=p["STEP_BG"])
                    sym_toggle_border.configure(bg=p["STEP_BORDER"])
                    num_toggle.configure(bg=p["ACCENT"], fg="#ffffff",
                                         activebackground=p["ACCENT_HOVER"],
                                         activeforeground="#ffffff")
                    sym_toggle.configure(bg=p["STEP_BG"], fg=p["TEXT_DIM"],
                                         activebackground=p["STEP_BG"],
                                         activeforeground=p["TEXT_BRIGHT"])

            sym_toggle.configure(command=lambda: _set_compute("symbolic"))
            num_toggle.configure(command=lambda: _set_compute("numerical"))

            # Error label (hidden initially)
            error_lbl = tk.Label(inner, text="", font=small_font,
                                 bg=p["STEP_BG"], fg=p["ERROR"],
                                 anchor="w", wraplength=350)
            error_lbl.pack(fill=tk.X, pady=(0, 4))

            def _submit_substitution(*_args):
                values = val_var.get().strip()
                if not values:
                    error_lbl.configure(text="Please enter variable values.")
                    return
                backdrop.destroy()
                modal.destroy()
                self._solve_with_mode(equation, "substitution",
                                      values_str=values,
                                      compute_mode=sub_compute_mode.get())

            val_entry.bind("<Return>", _submit_substitution)

            # Buttons row
            btn_row = tk.Frame(inner, bg=p["STEP_BG"])
            btn_row.pack(fill=tk.X, pady=(8, 0))

            action_btn_width = 11

            check_btn = tk.Button(
                btn_row, text="Check ➤", font=btn_font,
                bg=p["ACCENT"], fg="#ffffff",
                activebackground=p["ACCENT_HOVER"],
                activeforeground="#ffffff",
                bd=0, padx=14, pady=6, width=action_btn_width,
                cursor="hand2",
                command=_submit_substitution,
            )
            check_btn.pack(side=tk.LEFT)

            cancel_border = tk.Frame(
                btn_row,
                bg=p["INPUT_BORDER"],
                highlightbackground=p["INPUT_BORDER"],
                highlightthickness=1,
                bd=0,
            )
            cancel_border.pack(side=tk.RIGHT)

            cancel_kwargs = dict(
                text="Cancel",
                font=btn_font,
                bg=p["STEP_BG"],
                fg=p["TEXT_DIM"],
                activebackground=p["INPUT_BORDER"],
                activeforeground=p["TEXT_BRIGHT"],
                bd=0,
                padx=14,
                pady=6,
                width=action_btn_width,
                cursor="hand2",
                command=_cancel,
            )
            tk.Button(cancel_border, **cancel_kwargs).pack()

        def _cancel():
            backdrop.destroy()
            modal.destroy()

        btns = tk.Frame(inner, bg=p["STEP_BG"])
        btns.pack(fill=tk.X, pady=(0, 8))

        icon_font = tkfont.Font(family="Segoe UI Emoji", size=16)

        def _make_option_card(parent, icon, title, subtitle, on_click_fn):
            """Build a fully-clickable option card with whole-box hover."""
            border = tk.Frame(parent, bg=p["ACCENT"],
                              highlightbackground=p["ACCENT"],
                              highlightthickness=2, bd=0)
            border.pack(fill=tk.X, pady=4)
            card = tk.Frame(border, bg=p["STEP_BG"], padx=16, pady=12,
                            cursor="hand2")
            card.pack(fill=tk.X)

            # Row: icon + title
            row = tk.Frame(card, bg=p["STEP_BG"], cursor="hand2")
            row.pack(fill=tk.X)
            icon_lbl = tk.Label(row, text=icon, font=icon_font,
                                bg=p["STEP_BG"], fg=p["TEXT_BRIGHT"],
                                cursor="hand2")
            icon_lbl.pack(side=tk.LEFT, padx=(0, 8))
            title_lbl = tk.Label(row, text=title, font=btn_font,
                                 bg=p["STEP_BG"], fg=p["TEXT_BRIGHT"],
                                 cursor="hand2", anchor="w")
            title_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

            sub_lbl = tk.Label(card, text=subtitle, font=small_font,
                               bg=p["STEP_BG"], fg=p["TEXT_DIM"],
                               cursor="hand2", anchor="w")
            sub_lbl.pack(fill=tk.X, padx=(32, 0))

            # Collect all widgets so hover changes the whole card
            all_widgets = [card, row, icon_lbl, title_lbl, sub_lbl]

            def _on_enter(_evt):
                for w in all_widgets:
                    w.configure(bg=p["ACCENT"])
                icon_lbl.configure(fg="#ffffff")
                title_lbl.configure(fg="#ffffff")
                sub_lbl.configure(fg="#ffffff")

            def _on_leave(_evt):
                for w in all_widgets:
                    w.configure(bg=p["STEP_BG"])
                icon_lbl.configure(fg=p["TEXT_BRIGHT"])
                title_lbl.configure(fg=p["TEXT_BRIGHT"])
                sub_lbl.configure(fg=p["TEXT_DIM"])

            def _on_click(_evt):
                on_click_fn()

            for w in all_widgets:
                w.bind("<Enter>", _on_enter)
                w.bind("<Leave>", _on_leave)
                w.bind("<Button-1>", _on_click)

            border.bind("<Enter>", _on_enter)
            border.bind("<Leave>", _on_leave)
            border.bind("<Button-1>", _on_click)

        # Symbolic option
        _make_option_card(
            btns, "📐", "Symbolic Computation",
            "Exact answers — fractions, radicals, π  (SymPy)",
            lambda: _pick("symbolic"),
        )

        # Numerical option
        _make_option_card(
            btns, "🔢", "Numerical Computation",
            "Decimal approximations — floating-point  (NumPy)",
            lambda: _pick("numerical"),
        )

        # Substitution option
        _make_option_card(
            btns, "🔄", "Substitution Mode",
            "Plug in values to check if the equation holds  (SymPy)",
            _pick_substitution,
        )

        # Cancel link
        tk.Button(inner, text="Cancel", font=label_font,
                  bg=p["STEP_BG"], fg=p["TEXT_DIM"],
                  activebackground=p["STEP_BG"], activeforeground=p["TEXT_BRIGHT"],
                  bd=0, cursor="hand2", command=_cancel).pack(pady=(8, 0))

        # Close on backdrop click
        backdrop.bind("<Button-1>", lambda _: _cancel())

        # Close on Escape
        modal.bind("<Escape>", lambda _: _cancel())
        modal.focus_set()

    def _solve_with_mode(self, equation: str, mode: str,
                         values_str: str = "",
                         compute_mode: str = "symbolic") -> None:
        """Run the solve pipeline with the chosen mode."""
        if not (self._PHASE_PAUSE == 0 and self._TYPING_SPEED == 0):
            self._auto_scroll = True

        if hasattr(self, "_welcome_frame") and self._welcome_frame.winfo_exists():
            self._welcome_frame.destroy()

        self._entry.delete(0, tk.END)
        self._set_input_state(False)

        # For substitution mode, show both equation and values in the user bubble
        if mode == "substitution" and values_str:
            display_text = f"{equation}    [  {values_str}  ]"
        else:
            display_text = equation
        self._add_user_message(display_text)
        loading_label = self._add_loading()

        gen = self._solve_gen
        def _solve():
            try:
                result = solve_linear_equation(equation, mode=mode,
                                               values_str=values_str,
                                               compute_mode=compute_mode)
                self.after(0, lambda: self._show_result(result, loading_label)
                           if self._solve_gen == gen else None)
            except Exception as exc:
                msg = self._friendly_error(equation, exc)
                self.after(0, lambda: self._show_error(msg, loading_label)
                           if self._solve_gen == gen else None)

        threading.Thread(target=_solve, daemon=True).start()

    # ── Clear / reset ───────────────────────────────────────────────────

    def _clear_chat(self) -> None:
        self._anim_queue = []
        self._anim_idx = 0
        self._solve_gen += 1
        self._auto_scroll = True
        self._graph_panels.clear()
        for w in self._chat_frame.winfo_children():
            w.destroy()
        self._show_welcome()
        self._canvas.yview_moveto(0.0)
        self._set_input_state(True)
        self._entry.focus_set()

    # ── Send equation ───────────────────────────────────────────────────

    def _on_send(self) -> None:
        equation = self._entry.get().strip()
        if not equation:
            return
        self._show_solve_mode_modal(equation)

    @staticmethod
    def _friendly_error(equation: str, exc: Exception) -> str:
        msg = str(exc)
        if isinstance(exc, ValueError):
            if "Could not parse" in msg or "invalid syntax" in msg.lower():
                return (
                    f'Could not understand "{equation}".\n\n'
                    "Make sure your equation uses standard math notation.\n"
                    "Examples:  2x + 3 = 7  \u2022  as = 1  \u2022  x + y = 10, x - y = 2"
                )
            return msg
        return (
            f'DualSolver could not process "{equation}".\n\n'
            "Supports linear equations with one or more variables,\n"
            "and systems separated by commas or semicolons.\n"
            "Examples:  2x + 3 = 7  \u2022  2x + 4y = 1  \u2022  x+y=10, x-y=2\n\n"
            f"Details: {msg}"
        )

    def _stop_solving(self) -> None:
        self._anim_queue = []
        self._anim_idx = 0
        self._solve_gen += 1
        self._set_input_state(True)
        self._entry.focus_set()

    def _set_input_state(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        self._entry.configure(state=state)
        if enabled:
            self._stop_btn.pack_forget()
            self._send_btn.pack(fill=tk.BOTH, expand=True)
        else:
            if self._PHASE_PAUSE == 0 and self._TYPING_SPEED == 0:
                self._send_btn.pack_forget()
            else:
                self._send_btn.pack_forget()
                self._stop_btn.pack(fill=tk.BOTH, expand=True)

    # ── Chat bubbles ────────────────────────────────────────────────────

    def _add_user_message(self, text: str) -> None:
        rf = RoundedFrame(self._chat_frame, bg_color=themes.USER_BG,
                          corner_radius=themes.CORNER_RADIUS,
                          border_width=0, padding=6)
        rf.pack(fill=tk.X, padx=20, pady=(12, 4))
        frame = rf.inner
        frame.configure(padx=12, pady=8)
        tk.Label(frame, text="You", font=self._bold, bg=themes.USER_BG,
                 fg=themes.ACCENT, anchor="w").pack(fill=tk.X)
        tk.Label(frame, text=text, font=self._mono, bg=themes.USER_BG,
                 fg=themes.TEXT_BRIGHT, anchor="w").pack(fill=tk.X)
        if not (self._PHASE_PAUSE == 0 and self._TYPING_SPEED == 0):
            self._scroll_to_bottom()

    def _add_loading(self) -> tk.Label:
        label = tk.Label(
            self._chat_frame, text="  Processing…", font=self._default,
            bg=themes.BG, fg=themes.TEXT_DIM, anchor="w",
        )
        label.pack(fill=tk.X, padx=20, pady=6)
        if not (self._PHASE_PAUSE == 0 and self._TYPING_SPEED == 0):
            self._scroll_to_bottom()
        return label

    def _show_error(self, message: str, loading: tk.Label) -> None:
        loading.destroy()
        rf = RoundedFrame(self._chat_frame, bg_color=themes.BOT_BG,
                          corner_radius=themes.CORNER_RADIUS,
                          border_width=0, padding=6)
        rf.pack(fill=tk.X, padx=20, pady=(4, 12))
        frame = rf.inner
        frame.configure(padx=12, pady=8)
        tk.Label(frame, text="⚠  Error", font=self._bold, bg=themes.BOT_BG,
                 fg=themes.ERROR, anchor="w").pack(fill=tk.X)
        tk.Label(frame, text=message, font=self._default, bg=themes.BOT_BG,
                 fg=themes.TEXT, anchor="w", wraplength=880, justify=tk.LEFT
                 ).pack(fill=tk.X, pady=(6, 0))
        self._set_input_state(True)
        self._entry.focus_set()
        if not (self._PHASE_PAUSE == 0 and self._TYPING_SPEED == 0):
            self._scroll_to_bottom()


    # ── Toast notification ───────────────────────────────────────────

    def _show_toast(self, message: str, *, icon: str = "✓",
                    duration: int = 2500, kind: str = "success") -> None:
        """Show a brief toast notification in the top-right corner.

        *kind* can be ``"success"`` (green), ``"error"`` (red),
        or ``"info"`` (accent blue).
        """
        p = themes.palette(self._theme)
        fg_map = {
            "success": p["SUCCESS"],
            "error":   p["ERROR"],
            "info":    p["ACCENT"],
        }
        fg = fg_map.get(kind, p["SUCCESS"])

        toast = tk.Frame(
            self, bg=p["STEP_BG"],
            highlightbackground=fg, highlightthickness=1,
            padx=16, pady=10,
        )

        toast_font = tkfont.Font(family=self._ui_family, size=12, weight="bold")
        text = f"{icon}  {message}" if icon else message
        tk.Label(toast, text=text, font=toast_font,
                 bg=p["STEP_BG"], fg=fg).pack()

        # Place in top-right corner of the window
        self.update_idletasks()
        win_w = self.winfo_width()
        toast.update_idletasks()
        tw = toast.winfo_reqwidth()
        x = win_w - tw - 24
        y = 80                       # just below the header bar
        toast.place(x=x, y=y)
        toast.lift()                 # ensure it's above all other widgets

        # Reposition on window resize while toast is visible
        def _reposition(event=None):
            if toast.winfo_exists():
                toast.update_idletasks()
                new_x = self.winfo_width() - toast.winfo_reqwidth() - 24
                toast.place_configure(x=new_x)
        _resize_id = self.bind("<Configure>", _reposition, add="+")

        def _fade_out(alpha=1.0):
            if not toast.winfo_exists():
                return
            if alpha <= 0:
                self.unbind("<Configure>", _resize_id)
                toast.destroy()
                return
            try:
                toast.attributes  # Frames don't have attributes
            except Exception:
                pass
            # Simulate fade with stepped bg blending
            toast.after(40, lambda: _fade_out(alpha - 0.15))

        def _dismiss():
            if toast.winfo_exists():
                self.unbind("<Configure>", _resize_id)
                toast.destroy()

        self.after(duration, _dismiss)


def main() -> None:
    app = DualSolverApp()
    app.mainloop()


if __name__ == "__main__":
    main()
