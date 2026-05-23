# DualSolver

A desktop step-by-step solver for linear equations, built for COSC 110 (Numeric and Symbolic Computation) at Cavite State University – Imus.

---

## Features

- **Three solve modes** — Symbolic (SymPy, exact fractions/expressions), Numerical (NumPy, decimal approximations), and Substitution (verify whether specific values satisfy an equation).
- **Educational step trail** — every derivation step is labelled with the algebraic property applied (Distributive Property, Subtraction Property of Equality, Combining Like Terms, etc.).
- **Graph & Analysis card** — Matplotlib plot and case classification for single-variable linear equations.
- **Non-linear education** — non-linear inputs are detected and explained with the method that _would_ solve them (Quadratic Formula, Newton's Method, etc.) rather than crashing.
- **Export** — copy trail as plain text, save as HTML, or save as PDF with an embedded graph and result-interpretation block.
- **Solve history sidebar** — pin, archive, delete, and search past solves; capped at 200 entries, persists across sessions.
- **Six palettes** — Ocean Blue, Obsidian Black, Emerald Green, Sunset Orange, Crimson Red, Violet.
- **Robust input normalization** — full-width characters, Unicode minus/multiplication/division variants, smart quotes, and π/√ all normalize to ASCII before parsing.
- **Fully offline** — no accounts, no telemetry, no network calls. Everything lives in a single local JSON file.

---

## Project Structure

```text
DualSolver/
├── main.py                  # Three-line entry point
├── README.md
├── requirements.txt         # Runtime dependencies
├── requirements-dev.txt     # Dev/test dependencies (pytest)
├── .gitignore
│
├── gui/                     # Tkinter UI layer — no computation here
│   ├── __init__.py
│   ├── app.py               #   DualSolverApp (assembles all mixins)
│   ├── animation.py         #   AnimationMixin — animated step-card rendering
│   ├── widgets.py           #   WidgetMixin — section headers, cards, fraction renderer
│   ├── export.py            #   ExportMixin — clipboard / HTML / PDF export
│   ├── symbolpad.py         #   SymbolPadMixin — math symbol insertion pad
│   ├── settings.py          #   SettingsMixin — theme & animation preferences
│   ├── about.py             #   AboutMixin — in-app Help & About / User Guide
│   ├── sidebar.py           #   Sidebar — history panel (pin / archive / delete)
│   ├── storage.py           #   JSON persistence (data/dualsolver.json)
│   ├── themes.py            #   Six palette dicts + mutable colour shortcuts
│   ├── rounded.py           #   Hand-drawn rounded frame/button widgets
│   └── error_messages.py    #   Educational error text for solver failures
│
├── solver/                  # Pure Python computation — no Tkinter imports
│   ├── __init__.py
│   ├── engine.py            #   Mode dispatcher + backward-compat re-exports
│   ├── symbolic.py          #   SymPy solver (single-var, multi-var, system)
│   ├── numerical.py         #   NumPy solver (decimal results)
│   ├── substitution.py      #   Substitution verifier
│   └── graph.py             #   Matplotlib figures + case analysis
│
├── tests/                   # Pytest suite (110 collected, target ~107 passing)
│   ├── conftest.py          #   Sets Agg backend, prepends root to sys.path
│   ├── VALIDATION_RULES.md  #   Trail output contract (type map + validation rules)
│   └── test_*.py            #   8 test files covering math, storage, themes, graphs
│
├── assets/                  # Static assets
│   ├── logo.png
│   └── back.png
│
├── data/                    # Runtime data — gitignored except .gitkeep
│   └── .gitkeep
│
└── docs/                    # Documentation
    ├── user_guide.md        #   End-user guide (source of truth for in-app help)
    ├── process.md           #   Implementation walkthrough
    └── TESTING.md           #   Test plan and manual checklist
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/lncadrnn/DualSolver.git
cd DualSolver
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install runtime dependencies

```bash
pip install -r requirements.txt
```

Optional — enables the PNG logo in the header (falls back to a text label without it):

```bash
pip install pillow
```

### 4. Launch the app

```bash
python main.py
```

---

## Running Tests

Install dev dependencies first (once):

```bash
pip install -r requirements-dev.txt
```

```bash
pytest                                          # all tests, quiet
pytest -v                                       # verbose output
pytest tests/test_engine_unit.py                # single file
pytest -k "test_solve_linear_equation"          # by name pattern
```

`tests/conftest.py` sets `matplotlib.use("Agg")` and prepends the project root to `sys.path` so tests run headless without a display. Do not set a real Matplotlib backend in tests.

---

## Architecture

The codebase follows a strict two-layer split.

**Solver layer (`solver/`)** — pure Python, no Tkinter imports. `engine.py` is the single dispatch entry point: it routes by `mode` to `symbolic.py` (SymPy, exact answers), `numerical.py` (NumPy, decimal approximations), or `substitution.py` (value verification). `graph.py` builds Matplotlib figures from solver results. This layer is safe to import from tests or any Python context.

**GUI layer (`gui/`)** — Tkinter UI, imports `solver/`, never the other way around. `DualSolverApp` in `app.py` is assembled from six mixins (`AnimationMixin`, `WidgetMixin`, `ExportMixin`, `SymbolPadMixin`, `SettingsMixin`, `AboutMixin`) that keep features isolated by concern. Solves run on a background daemon thread; results are marshalled back to the main thread via `self.after(0, ...)`. Theme colors are live module-level attributes on `gui.themes` — reading `themes.BG` always returns the current palette value.

**Trail output contract** — every solve returns a dict with seven keys: `equation`, `given`, `method`, `steps`, `final_answer`, `verification_steps`, `summary`. Every step carries a `property` field naming the algebraic rule applied. The full schema and type map are in `tests/VALIDATION_RULES.md`.

**Storage** — `gui/storage.py` persists settings and history to `data/dualsolver.json`. History is capped at 200 entries; the file auto-recovers from corruption.

---

## Export Formats

| Format | How to trigger | Contents |
|---|---|---|
| **Plain text** | Copy to Clipboard | Full solve trail as UTF-8 text; paste into any editor or document. |
| **HTML** | Save as HTML | Self-contained HTML file with all trail sections and inline styling; open in any browser. |
| **PDF** | Save as PDF | Formatted PDF via fpdf2 with embedded graph image and a Result Interpretation metadata block. |

---

## Creators

- **Acal, Lance Adrian**
- **Garcia, Jesly Dinsen**
- **Moreno, Ryel Austin**

Built for COSC 110 — Numeric and Symbolic Computation, Cavite State University Imus, AY 2025–2026.

---

## License

All rights reserved. Academic use only.
