# DualSolver

**Version:** 1.0.0
**Course:** Numeric and Symbolic Computation (COSC 110) — Cavite State University, Imus

DualSolver is a desktop learning tool that solves linear equations step by step.
It supports three computation modes — **Symbolic** (exact), **Numerical** (decimal),
and **Substitution** (verify values) — and explains every algebraic move it makes
using the name of the property applied (Distributive, Subtraction Property of
Equality, Combining Like Terms, etc.).

The interface is a chat-style Tkinter app with a solid dark theme, six color
palettes, animated solution trails, embedded Matplotlib graphs, case analysis,
HTML/PDF export, and local solve history.

---

## Highlights

- **Three modes in one solver** — Symbolic (SymPy), Numerical (NumPy), Substitution (verify a guess).
- **Educational by design** — every step is labelled with the algebraic property it applies, every non-linear input gets an explanation of *why* it's non-linear and *what method would solve it* (Quadratic Formula, Newton's Method, etc.).
- **Robust to messy input** — full-width characters, Unicode minus / multiplication / division, smart quotes, and look-alikes all normalize to ASCII before parsing.
- **No accounts, no cloud** — every solve, every setting, every piece of history lives in a single local JSON file.
- **Exportable** — copy as plain text, save as HTML, or save as PDF (with embedded graph image and a "Result Interpretation" metadata block).
- **Six palettes** — Ocean Blue, Obsidian Black, Emerald Green, Sunset Orange, Crimson Red, Violet.

---

## Setup

### 1. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux (bash / zsh):**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Optional logo support (without it, the header shows a text label):

```bash
pip install pillow
```

### 3. Launch the app

```bash
python main.py
```

---

## Dependencies

| Package      | Min version | Purpose                                  |
| ------------ | ----------- | ---------------------------------------- |
| `sympy`      | 1.13        | Symbolic algebra engine                  |
| `numpy`      | 1.26        | Numerical linear algebra (matrix solve)  |
| `matplotlib` | 3.8         | Graph rendering inside the app           |
| `fpdf2`      | 2.8         | PDF export                               |
| `pytest`     | 8.0         | Automated test runner                    |
| `pillow`     | *(opt.)*    | Header logo (PNG); falls back to a label |

Tkinter ships with standard CPython on Windows and macOS — no separate install needed.

---

## Usage

1. Type a linear equation in the input bar.
2. Press **Enter** or click **Solve**.
3. Pick a computation mode in the modal:
   - **Symbolic** — exact answers using fractions / radicals / π (SymPy).
   - **Numerical** — decimal approximations (NumPy).
   - **Substitution** — provide variable values, then verify whether the equation holds.
4. Read the animated step-by-step trail. Each step shows the algebraic property used.
5. Expand the **Graph & Analysis** card for a visual + case classification.
6. Use **Copy to Clipboard**, **Save as HTML**, or **Save as PDF** to export.
7. Open the **sidebar** (hamburger ☰) for history (pin / archive / delete / clear).
8. **Settings** lets you switch palettes, change animation speed, and toggle auto-expand of verification / graph sections.
9. **About / Help** lives behind the `?` button in the header.

### Keyboard shortcuts

| Key      | Action                                              |
| -------- | --------------------------------------------------- |
| `Enter`  | Submit current input — opens the mode picker        |
| `Escape` | Close Settings / About / sidebar (context-aware)    |

### Supported input patterns

| Pattern                          | Example                  |
| -------------------------------- | ------------------------ |
| Single-variable linear equation  | `3x + 2 = 7`             |
| Single equation, many variables  | `2x + 4y = 1`            |
| System of equations              | `x + y = 10, x - y = 2`  |
| Substitution values              | `x = 3` or `x = 3, y = 4`|
| With constants π and √           | `x + π = 10`             |
| With fractions                   | `(1/2)x + 1 = 3`         |
| With decimal coefficients        | `0.5x + 1 = 3`           |

**Accepted operators and characters:** `+ - * / ^ = ( ) [ ] { } . , ; :`
plus single-letter variable names.

**Auto-normalized:** full-width characters (`２ｘ ＝ ４` → `2x = 4`),
Unicode minus / dash variants (`−`, `–`, `—`), multiplication / division
signs (`×`, `÷`), smart quotes, and π / √.

---

## Output contract

Every solve returns a dictionary with this structure:

```
equation, given, method, steps, final_answer, verification_steps, summary
```

- Each `steps[]` and `verification_steps[]` entry carries `step_number`,
  `description`, `expression`, `explanation`, and a `property` field naming
  the algebraic rule applied (e.g. *"Subtraction Property of Equality"*).
- `method.parameters` carries an `equation_type_code` — a machine-readable
  classifier (`linear_single_var`, `linear_system_2x2`,
  `linear_degenerate_identity`, `nonlinear_degree`, `nonlinear_denominator`,
  `nonlinear_product`, `nonlinear_transcendental`, `constant_tautology`,
  `constant_contradiction`, `substitution_true` / `_false` / `_indeterminate`).
- `summary` always includes `runtime_ms`, `total_steps`, `verification_steps`,
  `validation_status` (`"pass"` / `"fail"`), `timestamp`, and `library`.
- Non-linear inputs return `nonlinear_education: True` and a `validation_status`
  of `"fail"` — these are *educational responses*, not errors. The
  `final_answer` ends with a `→ ...` method-suggestion line.

Full validation rules and type maps: [`tests/VALIDATION_RULES.md`](tests/VALIDATION_RULES.md).

---

## Project structure

```text
DualSolver/
├─ main.py              # Three-line entry point
├─ requirements.txt
├─ README.md
├─ process.md           # Implementation walkthrough
├─ TESTING.md           # Test plan and manual checklist
├─ CLAUDE.md            # Codebase guide
├─ assets/              # Logo
├─ data/                # Local JSON (auto-created on first run)
├─ gui/                 # Tkinter UI (mixin-based)
│  ├─ app.py            #   Main window
│  ├─ animation.py      #   Step-by-step animated rendering
│  ├─ widgets.py        #   Section headers, cards, fraction renderer
│  ├─ export.py         #   Clipboard / HTML / PDF export
│  ├─ symbolpad.py      #   Symbol pad (≤, ≥, π, √, etc.)
│  ├─ settings.py       #   Theme + animation preferences
│  ├─ about.py          #   In-app Help & About
│  ├─ sidebar.py        #   History sidebar
│  ├─ storage.py        #   data/dualsolver.json persistence
│  ├─ themes.py         #   Six palette dicts + mutable shortcuts
│  └─ rounded.py        #   Hand-drawn rounded frame/button widgets
└─ solver/              # Pure Python — no Tkinter imports
   ├─ engine.py         #   Mode dispatcher
   ├─ symbolic.py       #   SymPy solver (single var, multi-var, system)
   ├─ numerical.py      #   NumPy solver (decimal results)
   ├─ substitution.py   #   Substitution verifier
   └─ graph.py          #   Matplotlib figures + case analysis
```

---

## Testing

```bash
pytest                                    # all tests
pytest -v                                 # verbose
pytest tests/test_engine_unit.py          # one file
pytest -k "test_solve_linear_equation"    # by name pattern
```

Target: **~97 passing tests** across eight files covering math correctness,
data validation, error handling, theming, graph generation, edge cases,
and the Phase-1 educational additions (property names, equation-type codes,
non-linear method hints, full substitution trail). See
[`TESTING.md`](TESTING.md) for the full test plan and manual checklist.

---

## Data storage & privacy

- All history and settings live in `data/dualsolver.json` (relative to the project root).
- No login, no telemetry, no cloud, no network calls.
- History is capped at 200 entries (oldest fall off automatically).
- The data file is human-readable; if it gets corrupted, the app falls back to defaults instead of crashing.

---

## Limitations (by design)

| Area                | What's not supported                                                                                              |
| ------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Equation type**   | Linear equations only. Quadratic / cubic / higher-degree, transcendental (`sin`, `cos`, `log`, `exp`), variables in denominators (`1/x`), and products of variables (`x·y`) are detected and explained but not solved. |
| **Visual style**    | Solid opaque panels by design — no OS blur / acrylic / mica effects.                                              |
| **Logo display**    | Requires `pillow`. Without it, the header shows a text label.                                                     |
| **Offline only**    | No cloud sync, no multi-device support, no account system.                                                        |
| **History cap**     | 200 entries maximum.                                                                                              |
| **Input length**    | 500 characters maximum per solve (`_MAX_INPUT_LENGTH` in `solver/symbolic.py`).                                   |
| **Themes**          | Six dark palettes. No light mode — the app is intentionally a dark-only experience.                              |

---

## Troubleshooting

| Symptom                                            | Fix                                                                                          |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `Parse error` on a valid-looking equation          | Ensure there is exactly one `=`; check for stray operators or unbalanced parentheses.        |
| App treats `x^2 + 1 = 0` as an error               | This is intentional — non-linear inputs return an educational explanation, not a solution.   |
| `Save as PDF` fails with a missing-module error    | Re-run `pip install -r requirements.txt`; the project requires `fpdf2 >= 2.8`.               |
| Header shows a text label instead of a logo        | Install Pillow: `pip install pillow`.                                                        |
| Pasting `２ｘ ＝ ４` gives "Invalid character"        | Update to v1.0+ — full-width characters are normalized to ASCII automatically.               |
| Settings reset themselves after a crash            | `data/dualsolver.json` was corrupted and rebuilt from defaults — your work isn't lost in memory; just re-export. |

---

## Creators

- **Acal, Lance Adrian**
- **Garcia, Jesly Dinsen**
- **Moreno, Ryel Austin**

Built for COSC 110 — Numeric and Symbolic Computation, Cavite State University Imus, AY 2025–2026.
