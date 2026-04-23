# DualSolver

Version: 1.0.0

DualSolver is a desktop learning tool for solving linear equations step by step.
It supports symbolic computation (exact values), numerical computation (decimal values),
and substitution checking. The interface is a chat-style Tkinter app with a solid dark style,
animated trails, graph/analysis cards, export options, and local solve history.

This project was developed for Numeric and Symbolic Computation (COSC 110)
at Cavite State University - Imus.

## Repository Review Summary

- The codebase is cleanly split into UI (`gui/`) and solver logic (`solver/`).
- Solve dispatch is centralized in `solver/engine.py` (`symbolic`, `numerical`, `substitution`).
- Trail output format is consistent across modes:
   `GIVEN -> METHOD -> STEPS -> FINAL ANSWER -> VERIFICATION -> SUMMARY`
   plus `GRAPH & ANALYSIS` in the GUI when applicable.
- Local persistence is file-based (`data/dualsolver.json`) with no external service dependency.
- Current test suite status (local): `53 passed`.

## Core Features

- Symbolic solving via SymPy for exact algebraic results.
- Numerical solving via NumPy for decimal approximations.
- Substitution mode to verify whether user-provided values satisfy an equation.
- Single-equation, multi-variable, and system-of-equations support.
- Non-linear input detection with educational feedback.
- Step-by-step trail generation with explanations.
- Verification steps and validation status in every solve result.
- Embedded Matplotlib graph and case analysis panel.
- Export solution trail to clipboard text and PDF.
- Sidebar history with pin, archive, delete, and clear operations.
- Settings page for animation speed and section auto-expand behavior.
- Symbol pad for quick math input.
- About/Help page (`?` button in header) with in-app guidance.

## Dependencies

Install from `requirements.txt`:

- `sympy>=1.13`
- `matplotlib>=3.8`
- `numpy>=1.26`
- `fpdf2>=2.8`
- `pytest>=8.0`

Notes:

- Tkinter is included with standard CPython on most desktop installs.
- Pillow is optional for loading PNG logos; without Pillow, the app falls back to text labels.

## How To Run

### 1. Create and activate a virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

macOS/Linux (bash/zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Optional logo support:

```bash
pip install pillow
```

### 3. Launch the app

```bash
python main.py
```

## How To Use The App

1. Enter an equation in the input bar (for systems, separate equations with `,` or `;`).
2. Click `Solve` or press `Enter`.
3. Choose a computation mode in the modal:
    `Symbolic`, `Numerical`, or `Substitution`.
4. Read the generated trail cards in order.
5. Expand/collapse graph and analysis when available.
6. Use `Copy to Clipboard` or `Save as PDF` to export results.
7. Open sidebar (`hamburger`) to review history, pin/archive items, or open settings.
8. Open the sidebar and choose `Help & About` for guidance.

Keyboard shortcuts:

- `Enter`: trigger solve flow
- `Escape`: close Settings/About/sidebar (context-aware)

## Supported Input Patterns

- Single-variable linear equation:
   `3x + 2 = 7`
- Single equation, multiple variables:
   `2x + 4y = 1`
- System of equations:
   `x + y = 10, x - y = 2`
- Substitution values format:
   `x = 3` or `x = 3, y = 4`

Accepted operators/symbols include:

- `+ - * / ^ = ( ) [ ] { } . , ; :`
- Unicode `pi` / `π` and `sqrt` / `√` are normalized internally.

## Output Contract

Each solve returns a dictionary with these top-level fields:

- `equation`
- `given`
- `method`
- `steps`
- `final_answer`
- `verification_steps`
- `summary`

`summary` includes runtime, step counts, validation status, timestamp, and computation library.

## Project Structure

```text
DualSolver/
|- main.py
|- README.md
|- process.md
|- requirements.txt
|- assets/
|- data/
|- gui/
|- solver/
`- tests/
```

Key modules:

- `solver/engine.py`: mode dispatcher and compatibility exports.
- `solver/symbolic.py`: SymPy-based symbolic solver and trail builder.
- `solver/numerical.py`: NumPy-based numerical solver and verification.
- `solver/substitution.py`: substitution checker workflow.
- `solver/graph.py`: graph rendering and case analysis.
- `gui/app.py`: main window and solve flow.
- `gui/about.py`: About/Help page.
- `gui/settings.py`: settings page.
- `gui/sidebar.py`: history and navigation.
- `gui/storage.py`: local JSON persistence.

## Testing

Run all tests:

```bash
pytest -q
```

Validation and expected data-contract checks are documented in:

- `tests/VALIDATION_RULES.md`

## Data Storage And Privacy

- All history and settings are stored locally in `data/dualsolver.json`.
- No login, cloud account, or remote database is required.

## Troubleshooting

- Parse error:
   Ensure input contains exactly one `=` for single equations and valid math symbols only.
- Non-linear detection:
   Inputs like `x^2`, `sin(x)`, `1/x`, or `x*y` are intentionally flagged as non-linear.
- PDF export error:
   Install `fpdf2` and retry.

## Creators

- Acal, Lance Adrian
- Garcia, Jesly Dinsen
- Moreno, Ryel Austin
