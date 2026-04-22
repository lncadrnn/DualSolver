"""
DualSolver — Export / clipboard mixin

Provides PDF/HTML export and plain-text clipboard copy.
"""

import base64
import html
import os
import re
import tempfile
import tkinter as tk
from tkinter import font as tkfont, filedialog, messagebox

from gui import themes


class ExportMixin:
    """Mixed into DualSolverApp — adds copy and file export actions."""

    def _notify_export_success(self, fmt: str) -> None:
        """Show a non-blocking success notice after file export."""
        if hasattr(self, "_show_toast"):
            self._show_toast(f"{fmt} exported!", icon="✓", kind="success")

    # ── Fraction normaliser (used by plain text and PDF) ───────────────

    @staticmethod
    def _frac_to_plain(text: str) -> str:
        """Convert fraction markers ⟦num|den⟧ to (num)/(den) for plain text."""
        return re.sub(r'⟦([^|⟧]+)\|([^⟧]+)⟧', r'(\1)/(\2)', text)

    @staticmethod
    def _result_type_label(result: dict) -> str:
        """Return Symbolic/Numerical/Substitution label for filenames."""
        method_name = str(result.get("method", {}).get("name", "")).lower()
        comp_label = str(
            result.get("given", {}).get("inputs", {}).get("computation", "")
        ).lower()

        if "substitution" in method_name or "substitution" in comp_label:
            return "Substitution"
        if "numerical" in method_name or "numerical" in comp_label or "numpy" in comp_label:
            return "Numerical"
        return "Symbolic"

    @staticmethod
    def _safe_equation_for_filename(equation: str) -> str:
        """Sanitize equation text for filesystem-safe file names."""
        compact = re.sub(r'\s+', '', str(equation).strip())
        compact = re.sub(r'[<>:"/\\|?*\n\r\t]', '', compact)
        if not compact:
            compact = "equation"
        return compact[:60]

    def _default_export_basename(self, result: dict) -> str:
        """Build base filename in DualSolver-Type-Equation format."""
        mode = self._result_type_label(result)
        eq = self._safe_equation_for_filename(result.get("equation", "equation"))
        return f"DualSolver-{mode}-{eq}"

    def _is_substitution_result(self, result: dict) -> bool:
        """Return True when the result came from substitution mode."""
        return self._result_type_label(result) == "Substitution"

    # ── Plain-text builder (clipboard) ─────────────────────────────────

    def _build_plain_text(self, result: dict) -> str:
        """Convert a solver result dict into a readable plain-text trail."""
        lines: list[str] = []
        lines.append("=" * 56)
        lines.append("  DualSolver — Solution Trail")
        lines.append("=" * 56)

        # GIVEN
        given = result.get("given", {})
        lines.append("\n── GIVEN ──────────────────────────────────")
        if given.get("problem"):
            lines.append(self._frac_to_plain(given["problem"]))
        for key, val in given.get("inputs", {}).items():
            label = key.replace("_", " ").title()
            lines.append(f"  {label}: {self._frac_to_plain(val)}")

        # METHOD
        method = result.get("method", {})
        lines.append("\n── METHOD ─────────────────────────────────")
        if method.get("name"):
            lines.append(f"  {method['name']}")
        if method.get("description"):
            lines.append(f"  {method['description']}")
        for key, val in method.get("parameters", {}).items():
            label = key.replace("_", " ").title()
            lines.append(f"  {label}: {val}")

        # STEPS
        steps = result.get("steps", [])
        lines.append("\n── STEPS ──────────────────────────────────")
        for step in steps:
            num = step.get("step_number", "?")
            lines.append(f"\n  Step {num}: {self._frac_to_plain(step.get('description', ''))}")
            if step.get("expression"):
                lines.append(f"    {self._frac_to_plain(step['expression'])}")
            if step.get("explanation"):
                lines.append(f"    → {self._frac_to_plain(step['explanation'])}")

        # FINAL ANSWER
        lines.append("\n── FINAL ANSWER ───────────────────────────")
        lines.append(f"  {self._frac_to_plain(result.get('final_answer', '?'))}")

        # VERIFICATION
        v_steps = result.get("verification_steps", [])
        if v_steps:
            lines.append("\n── VERIFICATION ───────────────────────────")
            for step in v_steps:
                num = step.get("step_number", "?")
                lines.append(f"\n  Step {num}: {self._frac_to_plain(step.get('description', ''))}")
                if step.get("expression"):
                    lines.append(f"    {self._frac_to_plain(step['expression'])}")
                if step.get("explanation"):
                    lines.append(f"    → {self._frac_to_plain(step['explanation'])}")

        # SUMMARY
        summary = result.get("summary", {})
        if summary:
            lines.append("\n── SUMMARY ────────────────────────────────")
            lines.append(f"  Runtime: {summary.get('runtime_ms', '?')} ms")
            lines.append(f"  Steps: {summary.get('total_steps', '?')}")
            lines.append(f"  Verification Steps: {summary.get('verification_steps', '?')}")
            lines.append(f"  Validation Status: {summary.get('validation_status', '?').upper()}")
            lines.append(f"  Timestamp: {summary.get('timestamp', '?')}")
            lines.append(f"  Library: {summary.get('library', '?')}")

        lines.append("\n" + "=" * 56)
        return "\n".join(lines)

    # ── Export bar (buttons below the solution) ────────────────────────

    def _add_export_bar(self, parent: tk.Frame, result: dict) -> None:
        """Add a copy/save action bar at the bottom of the bot message."""
        p = themes.palette(self._theme)
        bar = tk.Frame(parent, bg=p["BOT_BG"])
        bar.pack(fill=tk.X, pady=(12, 0))

        btn_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")

        copy_btn = tk.Button(
            bar, text="📋 Copy to Clipboard", font=btn_font,
            bg=p["STEP_BG"], fg=p["TEXT_BRIGHT"],
            activebackground=p["ACCENT"], activeforeground="#ffffff",
            bd=0, padx=14, pady=6, cursor="hand2", relief=tk.FLAT,
            command=lambda: self._copy_to_clipboard(result, copy_btn),
        )
        copy_btn.pack(side=tk.LEFT, padx=(0, 8))

        export_btn = tk.Button(
            bar, text="⬇ Export", font=btn_font,
            bg=p["STEP_BG"], fg=p["TEXT_BRIGHT"],
            activebackground=p["ACCENT"], activeforeground="#ffffff",
            bd=0, padx=14, pady=6, cursor="hand2", relief=tk.FLAT,
            command=lambda: self._show_export_menu(export_btn, result),
        )
        export_btn.pack(side=tk.LEFT)

    def _show_export_menu(self, anchor_btn: tk.Button, result: dict) -> None:
        """Open export format options (PDF/HTML) under the export button."""
        p = themes.palette(self._theme)
        menu = tk.Menu(
            self,
            tearoff=0,
            bg=p["STEP_BG"],
            fg=p["TEXT_BRIGHT"],
            activebackground=p["ACCENT"],
            activeforeground="#ffffff",
            bd=0,
        )
        menu.add_command(label="Save as PDF", command=lambda: self._save_as_pdf(result))
        menu.add_command(label="Save as HTML", command=lambda: self._save_as_html(result))

        # Keep a reference while the popup is active.
        self._export_menu = menu
        try:
            x = anchor_btn.winfo_rootx()
            y = anchor_btn.winfo_rooty() + anchor_btn.winfo_height()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    # ── Clipboard ──────────────────────────────────────────────────────

    def _copy_to_clipboard(self, result: dict, btn: tk.Button) -> None:
        """Copy the full solution trail as plain text to the clipboard."""
        text = self._build_plain_text(result)
        self.clipboard_clear()
        self.clipboard_append(text)
        original = btn.cget("text")
        btn.configure(text="✓ Copied!")
        self.after(1500, lambda: btn.configure(text=original))

    # ── File export helpers ────────────────────────────────────────────

    def _save_as_html(self, result: dict) -> None:
        """Export a full DualSolver-style HTML report (no action buttons)."""
        path = filedialog.asksaveasfilename(
            title="Save Solution as HTML",
            defaultextension=".html",
            initialfile=self._default_export_basename(result),
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
        )
        if not path:
            return

        def _esc(value) -> str:
            return html.escape(self._frac_to_plain(str(value)))

        def _esc_multiline(value) -> str:
            return _esc(value).replace("\n", "<br>")

        given = result.get("given", {})
        method = result.get("method", {})
        steps = result.get("steps", [])
        v_steps = result.get("verification_steps", [])
        summary = result.get("summary", {})

        mode_label = self._result_type_label(result)
        equation = result.get("equation", "")

        given_rows: list[str] = []
        if given.get("problem"):
            given_rows.append(
                f'<div class="line mono">{_esc(given.get("problem", ""))}</div>'
            )
        for key, val in given.get("inputs", {}).items():
            label = key.replace("_", " ").title()
            given_rows.append(
                f'<div class="kv"><span class="k">{html.escape(label)}</span>'
                f'<span class="v mono">{_esc(val)}</span></div>'
            )

        method_rows: list[str] = []
        if method.get("name"):
            method_rows.append(
                f'<div class="line strong">{_esc(method.get("name", ""))}</div>'
            )
        if method.get("description"):
            method_rows.append(
                f'<div class="line">{_esc_multiline(method.get("description", ""))}</div>'
            )
        for key, val in method.get("parameters", {}).items():
            label = key.replace("_", " ").title()
            method_rows.append(
                f'<div class="kv"><span class="k">{html.escape(label)}</span>'
                f'<span class="v mono">{_esc(val)}</span></div>'
            )

        step_cards: list[str] = []
        for step in steps:
            num = step.get("step_number", "?")
            card = [
                '<div class="step-card">',
                f'<div class="step-title">Step {html.escape(str(num))}: '
                f'{_esc(step.get("description", ""))}</div>'
            ]
            if step.get("expression"):
                card.append(f'<div class="expr mono">{_esc(step.get("expression", ""))}</div>')
            if step.get("explanation"):
                card.append(
                    f'<div class="explain">{_esc_multiline(step.get("explanation", ""))}</div>'
                )
            card.append("</div>")
            step_cards.append("".join(card))

        verify_cards: list[str] = []
        for step in v_steps:
            num = step.get("step_number", "?")
            card = [
                '<div class="step-card">',
                f'<div class="step-title">Step {html.escape(str(num))}: '
                f'{_esc(step.get("description", ""))}</div>'
            ]
            if step.get("expression"):
                card.append(f'<div class="expr mono">{_esc(step.get("expression", ""))}</div>')
            if step.get("explanation"):
                card.append(
                    f'<div class="explain">{_esc_multiline(step.get("explanation", ""))}</div>'
                )
            card.append("</div>")
            verify_cards.append("".join(card))

        summary_rows: list[str] = []
        if summary:
            summary_rows.extend([
                f'<div class="kv"><span class="k">Runtime</span><span class="v">{_esc(str(summary.get("runtime_ms", "?")) + " ms")}</span></div>',
                f'<div class="kv"><span class="k">Steps</span><span class="v">{_esc(summary.get("total_steps", "?"))}</span></div>',
                f'<div class="kv"><span class="k">Verification Steps</span><span class="v">{_esc(summary.get("verification_steps", "?"))}</span></div>',
                f'<div class="kv"><span class="k">Validation Status</span><span class="v">{_esc(str(summary.get("validation_status", "?")).upper())}</span></div>',
                f'<div class="kv"><span class="k">Timestamp</span><span class="v">{_esc(summary.get("timestamp", "?"))}</span></div>',
                f'<div class="kv"><span class="k">Library</span><span class="v">{_esc(summary.get("library", "?"))}</span></div>',
            ])

        graph_html = ""
        analysis_html = ""
        graph_analysis_block = ""
        graph_png_path = None
        try:
            from solver.graph import build_figure, analyze_result, restyle_figure, set_theme

            analysis = analyze_result(result)

            if not self._is_substitution_result(result):
                fig = build_figure(result)
                if fig is not None:
                    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    graph_png_path = tmp.name
                    tmp.close()

                    restyle_figure(fig, "light")
                    fig.savefig(graph_png_path, dpi=150, bbox_inches="tight",
                                facecolor="#ffffff", edgecolor="none")
                    set_theme("dark")

                    with open(graph_png_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode("ascii")
                    graph_html = (
                        '<div class="subhead">Graph</div>'
                        f'<img class="graph" alt="DualSolver graph" src="data:image/png;base64,{b64}">'
                    )

            if analysis:
                analysis_lines = [
                    f'<div class="line strong">{_esc(analysis.get("case_label", ""))}</div>',
                    f'<div class="line"><span class="k">General form:</span> {_esc(analysis.get("form", ""))}</div>',
                    f'<div class="line">{_esc_multiline(analysis.get("description", ""))}</div>',
                ]
                if analysis.get("detail"):
                    analysis_lines.append(
                        f'<div class="line"><span class="k">Condition:</span> {_esc(analysis.get("detail", ""))}</div>'
                    )
                if analysis.get("solution"):
                    analysis_lines.append(
                        f'<div class="line answer"><span class="k">Result:</span> {_esc(analysis.get("solution", ""))}</div>'
                    )
                analysis_html = (
                    '<div class="subhead">Analysis</div>'
                    f'{"".join(analysis_lines)}'
                )

            if graph_html or analysis_html:
                graph_analysis_block = (
                    '<section class="section">'
                    '<h2>Graph & Analysis</h2>'
                    f'{graph_html}'
                    f'{analysis_html}'
                    '</section>'
                )
        except Exception:
            pass
        finally:
            if graph_png_path:
                try:
                    os.remove(graph_png_path)
                except OSError:
                    pass

        verification_block = ""
        if verify_cards:
            verification_block = (
                '<section class="section">'
                '<h2>Verification</h2>'
                f'{"".join(verify_cards)}'
                '</section>'
            )

        summary_block = ""
        if summary_rows:
            summary_block = (
                '<section class="section">'
                '<h2>Summary</h2>'
                f'{"".join(summary_rows)}'
                '</section>'
            )

        html_text = (
            "<!doctype html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "  <meta charset=\"utf-8\">\n"
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "  <title>DualSolver Solution Trail</title>\n"
            "  <style>\n"
            "    :root { color-scheme: dark; }\n"
            "    body { margin: 0; padding: 24px; background: #0a0e1a; color: #e8ecf4; font-family: Segoe UI, Arial, sans-serif; }\n"
            "    .wrap { max-width: 1040px; margin: 0 auto; }\n"
            "    .hero { background: #101628; border: 1px solid #1e2848; border-radius: 14px; padding: 18px 20px; margin-bottom: 14px; }\n"
            "    .title { margin: 0; color: #0096C7; font-size: 24px; font-weight: 700; }\n"
            "    .subtitle { margin-top: 6px; color: #8090b0; font-size: 13px; }\n"
            "    .eq { margin-top: 8px; color: #e8ecf4; font-family: Consolas, monospace; font-size: 16px; }\n"
            "    .section { background: #101628; border: 1px solid #1e2848; border-radius: 14px; padding: 16px 18px; margin: 12px 0; }\n"
            "    h2 { margin: 0 0 10px; color: #00b4d8; font-size: 17px; }\n"
            "    .kv { display: grid; grid-template-columns: 190px 1fr; gap: 8px; margin: 6px 0; }\n"
            "    .k { color: #8090b0; font-weight: 600; }\n"
            "    .v { color: #e8ecf4; }\n"
            "    .line { margin: 6px 0; color: #e8ecf4; line-height: 1.45; }\n"
            "    .line.strong { font-weight: 700; }\n"
            "    .line.answer { color: #00e676; font-weight: 700; }\n"
            "    .mono { font-family: Consolas, monospace; }\n"
            "    .step-card { background: #0d1228; border: 1px solid #1e2848; border-radius: 10px; padding: 10px 12px; margin: 8px 0; }\n"
            "    .step-title { color: #e8ecf4; font-weight: 700; }\n"
            "    .expr { margin-top: 6px; color: #b8c0d8; }\n"
            "    .explain { margin-top: 6px; color: #8090b0; }\n"
            "    .answer-box { background: #081a14; border: 1px solid #00e676; color: #00e676; border-radius: 10px; padding: 10px 12px; font-weight: 700; }\n"
            "    .graph { width: 100%; height: auto; border-radius: 10px; border: 1px solid #1e2848; background: #ffffff; }\n"
            "    .subhead { margin: 10px 0 8px; color: #00b4d8; font-weight: 700; }\n"
            "  </style>\n"
            "</head>\n"
            "<body>\n"
            "  <div class=\"wrap\">\n"
            "    <header class=\"hero\">\n"
            "      <h1 class=\"title\">DualSolver - Solution Trail</h1>\n"
            f"      <div class=\"subtitle\">Mode: {html.escape(mode_label)}</div>\n"
            f"      <div class=\"eq\">{_esc(equation)}</div>\n"
            "    </header>\n"
            "    <section class=\"section\">\n"
            "      <h2>Given</h2>\n"
            f"      {''.join(given_rows)}\n"
            "    </section>\n"
            "    <section class=\"section\">\n"
            "      <h2>Method</h2>\n"
            f"      {''.join(method_rows)}\n"
            "    </section>\n"
            "    <section class=\"section\">\n"
            "      <h2>Steps</h2>\n"
            f"      {''.join(step_cards)}\n"
            "    </section>\n"
            "    <section class=\"section\">\n"
            "      <h2>Final Answer</h2>\n"
            f"      <div class=\"answer-box mono\">{_esc(result.get('final_answer', '?'))}</div>\n"
            "    </section>\n"
            f"    {verification_block}\n"
            f"    {graph_analysis_block}\n"
            f"    {summary_block}\n"
            "  </div>\n"
            "</body>\n"
            "</html>\n"
        )

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html_text)
        except OSError as exc:
            messagebox.showerror("Export error", f"Could not save HTML:\n{exc}")
        else:
            self._notify_export_success("HTML")

    # ── PDF export ─────────────────────────────────────────────────────

    def _save_as_pdf(self, result: dict) -> None:
        """Export the full solution trail as a styled PDF with graph & analysis."""
        path = filedialog.asksaveasfilename(
            title="Save Solution as PDF",
            defaultextension=".pdf",
            initialfile=self._default_export_basename(result),
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if not path:
            return

        import tempfile
        try:
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror("Missing dependency",
                                 "PDF export requires 'fpdf2'.\n\n"
                                 "Install it with:  pip install fpdf2")
            return

        # ── Set up PDF ──────────────────────────────────────────────
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()

        # Register Unicode fonts
        fonts_dir = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
        try:
            pdf.add_font("Arial", "", os.path.join(fonts_dir, "arial.ttf"))
            pdf.add_font("Arial", "B", os.path.join(fonts_dir, "arialbd.ttf"))
            pdf.add_font("Consolas", "", os.path.join(fonts_dir, "consola.ttf"))
            _font = "Arial"
            _mono = "Consolas"
        except Exception:
            _font = "Helvetica"
            _mono = "Courier"

        frac = self._frac_to_plain

        def safe(text: str) -> str:
            """Replace glyphs missing from embedded PDF fonts."""
            return (
                text
                .replace('\u2713', 'OK')    # ✓
                .replace('\u2714', 'OK')    # ✔
                .replace('\u27A4', '->')    # ➤
            )

        # ── Title ───────────────────────────────────────────────────
        pdf.set_font(_font, "B", 20)
        pdf.set_text_color(0, 150, 199)    # #0096C7 accent
        pdf.cell(0, 12, "DualSolver - Solution Trail", new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(0, 150, 199)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(6)

        def _section(title: str) -> None:
            pdf.ln(4)
            pdf.set_font(_font, "B", 13)
            pdf.set_text_color(26, 140, 255)
            pdf.cell(0, 8, safe(title), new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(26, 140, 255)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)

        def _label_value(label: str, value: str) -> None:
            pdf.set_font(_font, "B", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(40, 6, safe(f"{label}:"), new_x="END")
            pdf.set_font(_mono, "", 10)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 6, safe(f"  {frac(value)}"), new_x="LMARGIN", new_y="NEXT")

        def _body(text: str, bold: bool = False, size: int = 10) -> None:
            pdf.set_font(_font, "B" if bold else "", size)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 6, safe(frac(text)), new_x="LMARGIN", new_y="NEXT")

        def _mono_text(text: str, size: int = 10) -> None:
            pdf.set_font(_mono, "", size)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 6, safe(frac(text)), new_x="LMARGIN", new_y="NEXT")

        # ── GIVEN ───────────────────────────────────────────────────
        given = result.get("given", {})
        _section("GIVEN")
        if given.get("problem"):
            _body(frac(given["problem"]), bold=True)
        for key, val in given.get("inputs", {}).items():
            _label_value(key.replace("_", " ").title(), val)

        # ── METHOD ──────────────────────────────────────────────────
        method = result.get("method", {})
        _section("METHOD")
        if method.get("name"):
            _body(method["name"], bold=True, size=12)
        if method.get("description"):
            _body(method["description"])
        for key, val in method.get("parameters", {}).items():
            _label_value(key.replace("_", " ").title(), val)

        # ── STEPS ───────────────────────────────────────────────────
        _section("STEPS")
        for step in result.get("steps", []):
            num = step.get("step_number", "?")
            pdf.ln(2)
            _body(f"Step {num}: {frac(step.get('description', ''))}", bold=True)
            if step.get("expression"):
                _mono_text(f"    {frac(step['expression'])}")
            if step.get("explanation"):
                pdf.set_font(_font, "", 9)
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(0, 5, safe(f"    {frac(step['explanation'])}"), new_x="LMARGIN", new_y="NEXT")

        # ── FINAL ANSWER ────────────────────────────────────────────
        _section("FINAL ANSWER")
        pdf.set_font(_mono, "", 14)
        pdf.set_text_color(76, 175, 80)
        pdf.cell(0, 10, safe(frac(result.get("final_answer", "?"))), new_x="LMARGIN", new_y="NEXT")

        # ── VERIFICATION ────────────────────────────────────────────
        v_steps = result.get("verification_steps", [])
        if v_steps:
            _section("VERIFICATION")
            for step in v_steps:
                num = step.get("step_number", "?")
                pdf.ln(2)
                _body(f"Step {num}: {frac(step.get('description', ''))}", bold=True)
                if step.get("expression"):
                    _mono_text(f"    {frac(step['expression'])}")
                if step.get("explanation"):
                    pdf.set_font(_font, "", 9)
                    pdf.set_text_color(100, 100, 100)
                    pdf.multi_cell(0, 5, safe(f"    {frac(step['explanation'])}"), new_x="LMARGIN", new_y="NEXT")

        # ── GRAPH & ANALYSIS ────────────────────────────────────────
        graph_img_path = None
        try:
            from solver.graph import build_figure, analyze_result, restyle_figure, set_theme
            if not self._is_substitution_result(result):
                fig = build_figure(result)
                if fig is not None:
                    # Restyle to light theme so axis labels/ticks are visible
                    # on the white PDF background
                    restyle_figure(fig, "light")
                    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    fig.savefig(tmp.name, dpi=150, bbox_inches="tight",
                                facecolor="#ffffff", edgecolor="none")
                    tmp.close()
                    graph_img_path = tmp.name
                    # Restore dark palette so in-app graphs stay dark
                    set_theme("dark")

                    _section("GRAPH")
                    img_w = pdf.w - 20
                    pdf.image(graph_img_path, x=10, w=img_w)
                    pdf.ln(4)

            analysis = analyze_result(result)
            if analysis:
                _section("ANALYSIS")
                _body(analysis.get("case_label", ""), bold=True, size=12)
                pdf.ln(1)
                _body(f"General form: {analysis.get('form', '')}")
                pdf.ln(1)
                _body(analysis.get("description", ""))
                if analysis.get("detail"):
                    _body(f"Condition: {analysis['detail']}")
                if analysis.get("solution"):
                    pdf.ln(2)
                    pdf.set_font(_mono, "", 12)
                    pdf.set_text_color(76, 175, 80)
                    pdf.cell(0, 8, safe(f"Result: {frac(analysis['solution'])}"), new_x="LMARGIN", new_y="NEXT")
        except Exception:
            pass

        # ── SUMMARY ─────────────────────────────────────────────────
        summary = result.get("summary", {})
        if summary:
            _section("SUMMARY")
            _label_value("Runtime", f"{summary.get('runtime_ms', '?')} ms")
            _label_value("Steps", str(summary.get('total_steps', '?')))
            _label_value("Verification Steps", str(summary.get('verification_steps', '?')))
            _label_value("Validation Status", summary.get('validation_status', '?').upper())
            _label_value("Timestamp", summary.get('timestamp', '?'))
            _label_value("Library", summary.get('library', '?'))

        # ── Write ───────────────────────────────────────────────────
        try:
            pdf.output(path)
        except Exception as exc:
            messagebox.showerror("Export error", f"Could not save PDF:\n{exc}")
        else:
            self._notify_export_success("PDF")
        finally:
            if graph_img_path:
                try:
                    os.remove(graph_img_path)
                except OSError:
                    pass
