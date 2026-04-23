"""
DualSolver — Full-page settings mixin

Renders the settings overlay that replaces the chat view.
"""

import os
import tkinter as tk
from tkinter import ttk, font as tkfont

from gui import themes


class SettingsMixin:
    """Mixed into DualSolverApp — full-page settings panel."""

    def show_settings_page(self) -> None:
        """Replace chat content with a full-page settings view."""
        from gui.storage import get_settings, save_settings, clear_history, clear_all_data

        if getattr(self, '_about_visible', False):
            self.close_about_page()

        if hasattr(self, '_settings_frame') and self._settings_frame.winfo_exists():
            self._settings_frame.destroy()

        if not self._settings_visible:
            self._chat_wrapper.pack_forget()
            self._input_bar.pack_forget()
            self._settings_visible = True
            self._new_btn.pack_forget()

        p = themes.palette(self._theme)

        # Clean up any stale confirm overlays from a previous render.
        if hasattr(self, '_settings_confirm_modal'):
            try:
                if self._settings_confirm_modal is not None:
                    self._settings_confirm_modal.grab_release()
            except Exception:
                pass
            try:
                if self._settings_confirm_modal is not None and self._settings_confirm_modal.winfo_exists():
                    self._settings_confirm_modal.destroy()
            except Exception:
                pass
            self._settings_confirm_modal = None

        if hasattr(self, '_settings_confirm_backdrop'):
            try:
                if self._settings_confirm_backdrop is not None and self._settings_confirm_backdrop.winfo_exists():
                    self._settings_confirm_backdrop.destroy()
            except Exception:
                pass
            self._settings_confirm_backdrop = None

        self._settings_frame = tk.Frame(self._content, bg=p["BG"])
        self._settings_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollable inner
        settings_canvas = tk.Canvas(self._settings_frame, bg=p["BG"],
                                    highlightthickness=0)
        settings_sb = ttk.Scrollbar(self._settings_frame, orient=tk.VERTICAL,
                                    command=settings_canvas.yview,
                                    style=self._sb_style_name)
        settings_inner = tk.Frame(settings_canvas, bg=p["BG"])
        settings_canvas.create_window((0, 0), window=settings_inner, anchor="nw",
                                      tags="settings_inner")
        settings_canvas.configure(yscrollcommand=settings_sb.set)
        settings_sb.pack(side=tk.RIGHT, fill=tk.Y)
        settings_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def _update_settings_scroll(_=None):
            settings_canvas.configure(scrollregion=settings_canvas.bbox("all"))
            settings_canvas.update_idletasks()
            content_h = settings_inner.winfo_reqheight()
            canvas_h = settings_canvas.winfo_height()
            if content_h <= canvas_h:
                settings_sb.pack_forget()
            elif not settings_sb.winfo_ismapped():
                settings_sb.pack(side=tk.RIGHT, fill=tk.Y)

        settings_inner.bind("<Configure>", _update_settings_scroll)
        settings_canvas.bind(
            "<Configure>",
            lambda e: (settings_canvas.itemconfig("settings_inner", width=e.width),
                       _update_settings_scroll()))

        self._settings_canvas = settings_canvas

        def _settings_mousewheel(e):
            if settings_canvas.winfo_exists():
                settings_canvas.yview_scroll(int(-e.delta / 120), "units")

        self._settings_scroll_id = settings_canvas.bind_all(
            "<MouseWheel>", _settings_mousewheel)

        settings = get_settings()

        # Centered container
        center = tk.Frame(settings_inner, bg=p["BG"])
        center.pack(anchor="n", pady=(40, 40), padx=60, fill=tk.X)

        # ── Header row with back button ────────────────────────────
        header_row = tk.Frame(center, bg=p["BG"])
        header_row.pack(fill=tk.X, pady=(0, 20))

        _ui = getattr(self, '_ui_family', 'Segoe UI')

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
                    # Keep the icon compact in dense header rows.
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
                command=self.close_settings_page,
            ).pack(side=tk.LEFT)
        else:
            back_font = tkfont.Font(family=_ui, size=18)
            tk.Button(header_row, text="←", font=back_font,
                      bg=p["BG"], fg=p["TEXT_DIM"],
                      activebackground=p["BG"], activeforeground=p["TEXT_BRIGHT"],
                      bd=0, cursor="hand2", command=self.close_settings_page
                      ).pack(side=tk.LEFT)

        title_font = tkfont.Font(family=_ui, size=22, weight="bold")
        tk.Label(header_row, text="Settings", font=title_font,
                 bg=p["BG"], fg=p["TEXT_BRIGHT"]).pack(side=tk.LEFT, padx=(12, 0))

        # ── Card container ─────────────────────────────────────────
        from gui.rounded import RoundedFrame
        card_rf = RoundedFrame(center, bg_color=p["STEP_BG"],
                               border_color=p["STEP_BORDER"],
                               corner_radius=themes.CORNER_RADIUS,
                               border_width=1, padding=6)
        card_rf.pack(fill=tk.X)
        card = card_rf.inner
        card.configure(padx=24, pady=18)

        section_font = tkfont.Font(family=_ui, size=15, weight="bold")
        label_font   = tkfont.Font(family=_ui, size=13)
        small_font   = tkfont.Font(family=_ui, size=11)

        # ── Animation Speed ────────────────────────────────────────
        tk.Label(card, text="Animation Speed", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))

        speed_var = tk.StringVar(value=settings.get("animation_speed", "normal"))
        speed_frame = tk.Frame(card, bg=p["STEP_BG"])
        speed_frame.pack(fill=tk.X, pady=(0, 6))

        for val, label_text in [("slow", "🐢  Slow"), ("normal", "⚡  Normal"),
                                ("fast", "🚀  Fast"), ("instant", "⏭  Instant")]:
            rb_border = tk.Frame(speed_frame, bg=p["INPUT_BORDER"],
                                 highlightbackground=p["INPUT_BORDER"],
                                 highlightthickness=1, bd=0)
            rb_border.pack(fill=tk.X, pady=3)
            rb_inner = tk.Frame(rb_border, bg=p["STEP_BG"], padx=8, pady=5)
            rb_inner.pack(fill=tk.X)
            rb = tk.Radiobutton(
                rb_inner, text=label_text, variable=speed_var, value=val,
                font=label_font, bg=p["STEP_BG"], fg=p["TEXT_BRIGHT"],
                selectcolor=p["BG"], activebackground=p["STEP_BG"],
                activeforeground=p["ACCENT"],
                highlightthickness=0, bd=0, cursor="hand2",
            )
            rb.pack(anchor="w")

        # Divider
        tk.Frame(card, bg=p["TEXT_DIM"], height=1).pack(fill=tk.X, pady=(12, 12))

        # ── Display Options ────────────────────────────────────────
        tk.Label(card, text="Display", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))

        verify_var = tk.BooleanVar(value=settings.get("show_verification", False))
        cb1_border = tk.Frame(card, bg=p["INPUT_BORDER"],
                              highlightbackground=p["INPUT_BORDER"],
                              highlightthickness=1, bd=0)
        cb1_border.pack(fill=tk.X, pady=3)
        cb1_inner = tk.Frame(cb1_border, bg=p["STEP_BG"], padx=8, pady=5)
        cb1_inner.pack(fill=tk.X)
        tk.Checkbutton(
            cb1_inner, text="  Auto-expand verification section", variable=verify_var,
            font=label_font, bg=p["STEP_BG"], fg=p["TEXT_BRIGHT"],
            selectcolor=p["BG"], activebackground=p["STEP_BG"],
            activeforeground=p["ACCENT"],
            highlightthickness=0, bd=0, cursor="hand2",
        ).pack(anchor="w")

        graph_var = tk.BooleanVar(value=settings.get("show_graph", True))
        cb2_border = tk.Frame(card, bg=p["INPUT_BORDER"],
                              highlightbackground=p["INPUT_BORDER"],
                              highlightthickness=1, bd=0)
        cb2_border.pack(fill=tk.X, pady=3)
        cb2_inner = tk.Frame(cb2_border, bg=p["STEP_BG"], padx=8, pady=5)
        cb2_inner.pack(fill=tk.X)
        tk.Checkbutton(
            cb2_inner, text="  Auto-expand graph & analysis", variable=graph_var,
            font=label_font, bg=p["STEP_BG"], fg=p["TEXT_BRIGHT"],
            selectcolor=p["BG"], activebackground=p["STEP_BG"],
            activeforeground=p["ACCENT"],
            highlightthickness=0, bd=0, cursor="hand2",
        ).pack(anchor="w")

        # Divider
        tk.Frame(card, bg=p["TEXT_DIM"], height=1).pack(fill=tk.X, pady=(12, 12))

        # ── Color Theme ────────────────────────────────────────────
        tk.Label(card, text="Color Theme", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 6))
        tk.Label(card,
                 text="Pick a palette accent. This applies app-wide when you save.",
                 font=small_font, bg=p["STEP_BG"], fg=p["TEXT_DIM"]
                 ).pack(anchor="w", pady=(0, 10))

        theme_var = tk.StringVar(
            value=themes.normalize_theme(settings.get("theme", "dark"))
        )
        theme_choices = themes.available_themes()

        palette_grid = tk.Frame(card, bg=p["STEP_BG"])
        palette_grid.pack(fill=tk.X, pady=(0, 4))

        swatch_label_font = tkfont.Font(family=_ui, size=10, weight="bold")
        swatch_mark_font = tkfont.Font(family=_ui, size=11, weight="bold")
        swatches = {}

        def _set_theme_choice(theme_id: str) -> None:
            theme_var.set(theme_id)
            _refresh_theme_palette()

        def _refresh_theme_palette() -> None:
            selected = theme_var.get()
            for theme_id, data in swatches.items():
                canvas = data["canvas"]
                ring = data["ring"]
                mark = data["mark"]
                label = data["label"]
                if theme_id == selected:
                    canvas.itemconfigure(ring, outline=p["TEXT_BRIGHT"], width=3)
                    canvas.itemconfigure(mark, state="normal")
                    label.configure(fg=p["TEXT_BRIGHT"])
                else:
                    canvas.itemconfigure(ring, outline=p["STEP_BORDER"], width=2)
                    canvas.itemconfigure(mark, state="hidden")
                    label.configure(fg=p["TEXT_DIM"])

        columns = 3
        for col in range(columns):
            palette_grid.grid_columnconfigure(col, weight=1)

        for idx, item in enumerate(theme_choices):
            theme_id = item["id"]
            swatch_wrap = tk.Frame(palette_grid, bg=p["STEP_BG"], padx=8, pady=4)
            swatch_wrap.grid(row=idx // columns, column=idx % columns, sticky="w")

            swatch = tk.Canvas(
                swatch_wrap,
                width=44,
                height=44,
                bg=p["STEP_BG"],
                highlightthickness=0,
                bd=0,
                cursor="hand2",
            )
            swatch.pack(anchor="w")

            ring_id = swatch.create_oval(
                4, 4, 40, 40,
                fill=item["accent"],
                outline=p["STEP_BORDER"],
                width=2,
            )
            swatch.create_oval(14, 14, 30, 30, fill=p["BG_DARKER"], outline="")
            mark_id = swatch.create_text(
                22, 22,
                text="✓",
                fill=item.get("accent_text", "#ffffff"),
                font=swatch_mark_font,
                state="hidden",
            )

            swatch_label = tk.Label(
                swatch_wrap,
                text=item["label"],
                font=swatch_label_font,
                bg=p["STEP_BG"],
                fg=p["TEXT_DIM"],
            )
            swatch_label.pack(anchor="w", pady=(4, 0))

            swatches[theme_id] = {
                "canvas": swatch,
                "ring": ring_id,
                "mark": mark_id,
                "label": swatch_label,
            }

            for widget in (swatch_wrap, swatch, swatch_label):
                widget.bind("<Button-1>",
                            lambda _e, t=theme_id: _set_theme_choice(t))

        _refresh_theme_palette()

        # ── Save button + message ──────────────────────────────────
        bottom = tk.Frame(card, bg=p["STEP_BG"])
        bottom.pack(fill=tk.X, pady=(20, 0))

        msg_label = tk.Label(bottom, text="", font=small_font,
                             bg=p["STEP_BG"], fg=p["SUCCESS"])
        msg_label.pack(anchor="w", pady=(0, 8))

        def _save():
            new_settings = {
                "theme": themes.normalize_theme(theme_var.get()),
                "animation_speed": speed_var.get(),
                "show_verification": verify_var.get(),
                "show_graph": graph_var.get(),
            }
            save_settings(new_settings)
            self._sidebar._apply_settings_to_app(new_settings)

            if hasattr(self, "_settings_canvas") and self._settings_canvas.winfo_exists():
                try:
                    self._settings_scroll_pos = self._settings_canvas.yview()[0]
                except Exception:
                    self._settings_scroll_pos = 0.0

            self._rebuild_settings_with_scroll()
            self._show_toast("Settings saved!")

        save_font = tkfont.Font(family=_ui, size=14, weight="bold")
        tk.Button(bottom, text="Save Settings", font=save_font,
                  bg=p["ACCENT"], fg=p["ACCENT_TEXT"],
                  activebackground=p["ACCENT_HOVER"],
                  activeforeground=p["ACCENT_TEXT"],
                  bd=0, padx=24, pady=10, cursor="hand2",
                  command=_save).pack(fill=tk.X)

        # ── Data Management card ───────────────────────────────────
        data_rf = RoundedFrame(center, bg_color=p["STEP_BG"],
                               border_color=p["STEP_BORDER"],
                               corner_radius=themes.CORNER_RADIUS,
                               border_width=1, padding=6)
        data_rf.pack(fill=tk.X, pady=(20, 0))
        data_card = data_rf.inner
        data_card.configure(padx=24, pady=18)

        tk.Label(data_card, text="Data Management", font=section_font,
                 bg=p["STEP_BG"], fg=p["ACCENT"]).pack(anchor="w", pady=(0, 8))

        tk.Label(data_card, text="Manage your locally stored solve history and settings.",
                 font=small_font, bg=p["STEP_BG"],
                 fg=p["TEXT_DIM"]).pack(anchor="w", pady=(0, 12))

        data_msg = tk.Label(data_card, text="", font=small_font,
                            bg=p["STEP_BG"], fg=p["SUCCESS"])
        data_msg.pack(anchor="w", pady=(0, 8))

        # ── Clear History button ───────────────────────────────────
        def _clear_hist():
            clear_history()
            data_msg.configure(text="✓  History cleared!", fg=p["SUCCESS"])
            self._show_toast("History cleared!", icon="🗑")
            self.after(3000, lambda: data_msg.configure(text="")
                       if data_msg.winfo_exists() else None)

        def _confirm_clear_hist():
            _show_confirm_modal(
                "Clear all solve history?",
                "This will permanently delete all history entries.",
                "Clear History", _clear_hist,
            )

        btn_font = tkfont.Font(family=_ui, size=13, weight="bold")

        clear_hist_border = tk.Frame(data_card, bg=p["INPUT_BORDER"],
                                     highlightbackground=p["INPUT_BORDER"],
                                     highlightthickness=1, bd=0)
        clear_hist_border.pack(fill=tk.X, pady=3)
        tk.Button(clear_hist_border, text="🗑  Clear History", font=btn_font,
                  bg=p["STEP_BG"], fg=p["TEXT_BRIGHT"],
                  activebackground=p["INPUT_BORDER"],
                  activeforeground=p["TEXT_BRIGHT"],
                  bd=0, padx=14, pady=10, cursor="hand2", anchor="w",
                  command=_confirm_clear_hist).pack(fill=tk.X)

        # ── Reset All Data button ──────────────────────────────────
        def _reset_all():
            clear_all_data()
            self._sidebar._apply_user_settings()
            data_msg.configure(text="✓  All data reset!", fg=p["SUCCESS"])
            self._show_toast("All data reset!", icon="⚠", kind="info")
            self.after(1500, lambda: (
                self._rebuild_settings_with_scroll()
                if self._settings_visible else None))

        def _confirm_reset():
            _show_confirm_modal(
                "Reset all data?",
                "This will erase all history AND reset settings to defaults.",
                "Reset Everything", _reset_all,
                danger=True,
            )

        reset_border = tk.Frame(data_card, bg=p["ERROR"],
                                highlightbackground=p["ERROR"],
                                highlightthickness=1, bd=0)
        reset_border.pack(fill=tk.X, pady=(8, 3))
        tk.Button(reset_border, text="⚠  Reset All Data", font=btn_font,
                  bg=p["STEP_BG"], fg=p["ERROR"],
                  activebackground=p["ERROR"],
                  activeforeground="#ffffff",
                  bd=0, padx=14, pady=10, cursor="hand2", anchor="w",
                  command=_confirm_reset).pack(fill=tk.X)

        # ── Confirmation helper (modal overlay) ────────────────────
        def _show_confirm_modal(title, desc, btn_text, action, danger=False):
            """Show a centered confirmation modal that never duplicates."""
            _close_confirm_modal()

            backdrop = tk.Frame(self._settings_frame, bg="#050810")
            backdrop.place(relx=0, rely=0, relwidth=1, relheight=1)
            backdrop.lift()

            border_color = p["ERROR"] if danger else p["ACCENT"]
            modal = tk.Frame(
                self._settings_frame,
                bg=p["STEP_BG"],
                highlightbackground=border_color,
                highlightthickness=2,
                bd=0,
                padx=0,
                pady=0,
            )
            modal.place(relx=0.5, rely=0.5, anchor="center")
            modal.lift()

            self._settings_confirm_backdrop = backdrop
            self._settings_confirm_modal = modal

            inner = tk.Frame(modal, bg=p["STEP_BG"], padx=30, pady=22)
            inner.pack()

            title_font = tkfont.Font(family=_ui, size=15, weight="bold")
            tk.Label(
                inner,
                text=title,
                font=title_font,
                bg=p["STEP_BG"],
                fg=p["ERROR"] if danger else p["TEXT_BRIGHT"],
                anchor="w",
                justify=tk.LEFT,
                wraplength=440,
            ).pack(fill=tk.X)

            tk.Label(
                inner,
                text=desc,
                font=small_font,
                bg=p["STEP_BG"],
                fg=p["TEXT_DIM"],
                anchor="w",
                justify=tk.LEFT,
                wraplength=440,
            ).pack(fill=tk.X, pady=(6, 14))

            btn_row = tk.Frame(inner, bg=p["STEP_BG"])
            btn_row.pack(fill=tk.X)
            btn_center = tk.Frame(btn_row, bg=p["STEP_BG"])
            btn_center.pack(anchor="center")

            def _run_action():
                _close_confirm_modal()
                action()

            tk.Button(
                btn_center,
                text=btn_text,
                font=btn_font,
                bg=p["ERROR"] if danger else p["ACCENT"],
                fg="#ffffff" if danger else p["ACCENT_TEXT"],
                activebackground="#cc0000" if danger else p["ACCENT_HOVER"],
                activeforeground="#ffffff" if danger else p["ACCENT_TEXT"],
                bd=0,
                padx=16,
                pady=7,
                cursor="hand2",
                command=_run_action,
            ).pack(side=tk.LEFT, padx=(0, 8))

            cancel_border = tk.Frame(
                btn_center,
                bg=p["INPUT_BORDER"],
                highlightbackground=p["INPUT_BORDER"],
                highlightthickness=1,
                bd=0,
            )
            cancel_border.pack(side=tk.LEFT, padx=(8, 0))

            tk.Button(
                cancel_border,
                text="Cancel",
                font=btn_font,
                bg=p["STEP_BG"],
                fg=p["TEXT_DIM"],
                activebackground=p["INPUT_BORDER"],
                activeforeground=p["TEXT_BRIGHT"],
                bd=0,
                padx=16,
                pady=7,
                cursor="hand2",
                command=_close_confirm_modal,
            ).pack()

            backdrop.bind("<Button-1>", lambda _e: _close_confirm_modal())
            modal.bind("<Escape>", lambda _e: _close_confirm_modal())
            modal.focus_set()
            try:
                modal.grab_set()
            except Exception:
                pass

        def _close_confirm_modal():
            """Close the active confirm modal if present."""
            modal = getattr(self, '_settings_confirm_modal', None)
            backdrop = getattr(self, '_settings_confirm_backdrop', None)

            if modal is not None:
                try:
                    modal.grab_release()
                except Exception:
                    pass
                try:
                    if modal.winfo_exists():
                        modal.destroy()
                except Exception:
                    pass

            if backdrop is not None:
                try:
                    if backdrop.winfo_exists():
                        backdrop.destroy()
                except Exception:
                    pass

            self._settings_confirm_modal = None
            self._settings_confirm_backdrop = None

    def _rebuild_settings_with_scroll(self) -> None:
        """Rebuild settings page and restore saved scroll position."""
        saved = getattr(self, '_settings_scroll_pos', None)
        self.show_settings_page()
        if saved is not None:
            def _restore():
                if hasattr(self, '_settings_canvas') and self._settings_canvas.winfo_exists():
                    self._settings_canvas.update_idletasks()
                    self._settings_canvas.yview_moveto(saved)
            self.after(80, _restore)

    def close_settings_page(self) -> None:
        """Destroy the settings page and restore the chat view."""
        if not self._settings_visible:
            return

        modal = getattr(self, '_settings_confirm_modal', None)
        backdrop = getattr(self, '_settings_confirm_backdrop', None)
        if modal is not None:
            try:
                modal.grab_release()
            except Exception:
                pass
            try:
                if modal.winfo_exists():
                    modal.destroy()
            except Exception:
                pass
            self._settings_confirm_modal = None
        if backdrop is not None:
            try:
                if backdrop.winfo_exists():
                    backdrop.destroy()
            except Exception:
                pass
            self._settings_confirm_backdrop = None

        if hasattr(self, '_settings_scroll_id') and hasattr(self, '_settings_canvas'):
            try:
                self._settings_canvas.unbind_all("<MouseWheel>")
                self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
            except Exception:
                pass
        if hasattr(self, '_settings_frame') and self._settings_frame.winfo_exists():
            self._settings_frame.destroy()
        self._settings_visible = False
        self._chat_wrapper.pack(fill=tk.BOTH, expand=True)
        self._input_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self._new_btn.pack(side=tk.RIGHT, padx=(0, 20), pady=16)
        self._entry.focus_set()
