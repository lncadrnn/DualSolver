# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

DualSolver is a Tkinter desktop app for solving linear equations step-by-step, built for COSC 110 at Cavite State University - Imus. It is a pure-Python, offline tool — no server, no API layer, no accounts. Solver logic and GUI live in the same process.

## Commands

```bash
# Setup (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run the app
python main.py

# Run tests (target: 67 passing)
pytest                                  # all tests, quiet
pytest -v                               # verbose
pytest tests/test_engine_unit.py        # one file
pytest -k "test_solve_linear_equation_required_fields"  # by name
```

`tests/conftest.py` sets `matplotlib.use("Agg")` and prepends the project root to `sys.path`, so tests run headless without an X server. Don't add a real backend in tests — graph tests assert figures can build under Agg.

Optional: `pip install pillow` enables the PNG logo in the header; without it the app falls back to a text label.

## Architecture

### Two-layer split

- `solver/` — pure computation, no Tk imports. Safe to import from anywhere.
- `gui/` — Tkinter UI. Imports `solver`, never the other way around.
- `main.py` — three-line entry point that constructs `DualSolverApp` and runs `mainloop()`.

### Solver dispatch (`solver/engine.py`)

`solve_linear_equation(equation_str, *, mode, values_str, compute_mode)` is the single entry point used by both the GUI and tests. It routes by `mode`:

- `"symbolic"` (default) → `solver/symbolic.py` (SymPy, exact answers)
- `"numerical"` → `solver/numerical.py` (NumPy, decimals)
- `"substitution"` → `solver/substitution.py` (plug values into an equation and verify)

`engine.py` re-exports a long list of private helpers (`_detect_variables`, `_format_equation`, `_nonlinear_error_result`, etc.) from `solver.symbolic` for backward compatibility — tests and the graph module import these via `solver.engine`. When refactoring symbolic.py, keep the re-export list in engine.py in sync, otherwise tests will break.

### Trail output contract

Every solve returns a dict with exactly these top-level keys:

```
equation, given, method, steps, final_answer, verification_steps, summary
```

`summary` always contains `runtime_ms`, `total_steps`, `verification_steps`, `validation_status` (`"pass"`/`"fail"`), `timestamp`, `library`. The full type map and validation rules are in `tests/VALIDATION_RULES.md` — this is the contract tests enforce, so changes to result shape need test updates.

The GUI also renders a `warnings` list (when present) and a Graph & Analysis card built from `solver/graph.py`. Non-linear inputs return a result with `nonlinear_education: True` and a `validation_status: "fail"` — they are *not* errors, they are educational responses.

**Phase-1 schema additions (post-2026-05):**

- Every `steps[]` entry (and `verification_steps[]`) carries an extra `property` field naming the algebraic rule applied (e.g. `"Subtraction Property of Equality"`, `"Distributive Property"`, `"Combining Like Terms"`). Educational consumers can render this; existing consumers ignore it.
- `method.parameters` now also carries `equation_type_code` — a machine-readable classifier (`linear_single_var`, `linear_system_2x2`, `linear_degenerate_identity`, `nonlinear_degree`, `nonlinear_denominator`, `nonlinear_product`, `nonlinear_transcendental`, `constant_tautology`, `constant_contradiction`, `substitution_true`/`false`/`indeterminate`, etc.). Exports drive their "Result Interpretation" block from this; keep new codes mapped in `gui/export.py:ExportMixin._EQ_TYPE_HUMAN`.
- **Substitution mode now populates `verification_steps`** (was always `[]` pre-Phase-1) and writes `summary.verification_steps`. Three outcomes: `true` / `false` / `indeterminate` (when the substitution leaves free variables).

### GUI composition

`DualSolverApp` in `gui/app.py` is built from mixins (`AnimationMixin`, `WidgetMixin`, `ExportMixin`, `SymbolPadMixin`, `SettingsMixin`, `AboutMixin`) plus `tk.Tk`. Each mixin lives in its own file under `gui/`. When adding a new top-level feature (export format, settings page, etc.), prefer extending the relevant mixin rather than stuffing more into `app.py`.

Solves run on a daemon thread (`gui/app.py:_solve_with_mode`) so the GUI stays responsive. Results are marshalled back to the main thread via `self.after(0, ...)`. A monotonically increasing `self._solve_gen` counter cancels stale results when the user clicks Stop or New Chat.

Theme colors are mutable module-level attributes on `gui.themes` (e.g. `themes.BG`, `themes.ACCENT`). `themes.palette("light"|"dark")` returns a dict; `apply_theme()` rebinds the module attributes. This is why imports like `from gui import themes; tk.Label(bg=themes.BG)` work — they read the live attribute. Don't capture `themes.BG` into a local at module load time; it won't update on theme switch.

### Storage

`gui/storage.py` persists settings and solve history to `data/dualsolver.json` (relative to the project root). It handles corrupt-JSON recovery (falls back to defaults) and migrates a legacy `{"users": ..., "guest_settings": ...}` shape. History is capped at 200 entries. There is no cloud sync.

### Stale file warning

`head_app.py` at the project root is an older, near-duplicate copy of `gui/app.py`. It is **not** imported anywhere (`main.py` → `gui.__init__` → `gui.app`). Don't edit it — change `gui/app.py` instead. If touching the entry point, double-check imports point to `gui/app.py`.

## Conventions worth knowing

- Input length is hard-capped at 500 chars (`_MAX_INPUT_LENGTH` in `solver/symbolic.py`); over that raises before parsing.
- Unicode `π` and `√` are normalized to `pi` / `sqrt` inside the solver; the GUI prettifies them back for display.
- Full-width / look-alike characters (`２ｘ ＝ ４`, `−`, `–`, `×`, `÷`, smart quotes) are normalized to ASCII via `_normalize_unicode` *before* `_validate_characters`. Don't add another character-rejection layer that runs before normalization — it will reject perfectly valid pasted input.
- `_validate_equation_structure` runs after character validation. It rejects repeated `=`, empty segments between separators, hanging operators, and triple operator runs. SymPy never sees malformed input from this path.
- `^` is rewritten to `**` before SymPy sees it.
- Implicit multiplication is enabled (`as` → `a*s`) via SymPy's `implicit_multiplication_application` transformation. This is intentional and tested — don't disable it.
- Edge cases that look like errors but are actually valid results: tautologies (`5 = 5`), contradictions (`3 = 7`), identities (`x = x`). These return a trail with warnings, not exceptions. See `tests/test_edge_cases_unit.py` and `tests/test_phase1_improvements.py`.
- Non-linear `final_answer` strings end with a `→ ...` method-suggestion line and a `Scope note:` paragraph. The educational message is part of the contract; tests assert specific keywords are present (e.g. "Quadratic Formula" for degree 2). Re-word carefully.
