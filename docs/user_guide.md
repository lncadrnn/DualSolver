# DualSolver — User Guide

**Version:** 1.0.0  
**Course:** COSC 110 — Numeric and Symbolic Computation, Cavite State University – Imus

---

## Overview

DualSolver is a desktop application for solving linear equations step by step. It supports three computation modes and explains every algebraic move it makes, making it suitable for learning as well as verification. The app is fully offline — no internet connection or account is required.

**What it can solve:**

- Single-variable linear equations (`3x + 2 = 7`)
- Multi-variable linear equations (`2x + 4y = 1`)
- Systems of two linear equations (`x + y = 10, x - y = 2`)
- Substitution verification (check whether given values satisfy an equation)

**What it does not solve** (but explains):

- Quadratic and higher-degree equations
- Transcendental equations (`sin(x) = 0.5`, `log(x) = 2`)
- Equations with variables in denominators (`1/x = 3`)
- Equations with products of variables (`x·y = 6`)

For non-linear input, DualSolver returns an educational explanation of why it is non-linear and which method would solve it.

---

## Installation

### Requirements

- Python 3.10 or later
- Tkinter (bundled with standard CPython on Windows and macOS)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/lncadrnn/SymSolver.git
cd SymSolver

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Optional: install Pillow for the PNG logo
pip install pillow

# 5. Run
python main.py
```

---

## Interface Overview

The application window has four main areas:

| Area | Location | Purpose |
|---|---|---|
| **Input bar** | Bottom center | Type your equation here; press Enter or click Solve |
| **Results area** | Center | Displays the animated step-by-step solve trail |
| **Sidebar** | Left (☰ icon) | Browse and manage your solve history |
| **Symbol pad** | Keyboard icon near input bar | Insert math symbols at the cursor with one click |

---

## Usage

### Basic workflow

1. Type an equation in the input bar.
2. Press **Enter** or click **Solve**.
3. A popup asks which mode to use — pick one (see [Solve Modes](#solve-modes) below).
4. Read the animated trail cards in order.
5. Expand the **Graph & Analysis** card for a visual and case classification (single-variable equations only).
6. Export the result if needed (see [Export](#export)).

### Keyboard shortcuts

| Key | Action |
|---|---|
| `Enter` | Submit the equation in the input bar |
| `Escape` | Close the active panel (Settings, Help & About, or Sidebar) |

---

## Entering Equations

Type directly into the input bar. Accepted formats:

| Pattern | Example |
|---|---|
| Single variable | `3x + 2 = 7` |
| Two variables | `2x + 4y = 1` |
| System of two equations | `x + y = 10, x - y = 2` |
| Parentheses | `2(x + 3) = 14` |
| Fractions | `x/2 + 1 = 3` |
| Exponents | `x^2 + x = 6` *(non-linear — explained, not solved)* |

**Separators:** Use a comma (`,`) or semicolon (`;`) to separate the two equations in a system.

**Auto-normalized input** — the following are accepted and converted automatically:

- Full-width characters: `２ｘ ＝ ４` → `2x = 4`
- Unicode minus/dash variants: `−`, `–`, `—` → `-`
- Unicode operators: `×` → `*`, `÷` → `/`
- Math constants: `π` → `pi`, `√` → `sqrt`
- Smart quotes: `"`, `"`, `'`, `'` → `"`, `'`

**Input limit:** 500 characters.

---

## Solve Modes

After pressing Solve, a popup asks which mode to use.

### Symbolic *(recommended for learning)*

Uses **SymPy** to compute exact answers — fractions, radicals, and symbolic expressions.

- Shows every algebraic step with the property name applied to each.
- Best for understanding the solution process.
- Example output: `x = 5/3`

### Numerical

Uses **NumPy** to compute decimal approximations.

- Faster for getting a quick numeric answer.
- Fewer intermediate steps shown.
- Example output: `x = 1.6667`

### Substitution

Checks whether specific values satisfy the equation.

**How to use:**

1. Enter the equation in the input bar (e.g. `2x + y = 8`).
2. Select **Substitution** from the mode popup.
3. A **Values** field appears — enter the values to test:
   ```
   x = 3, y = 2
   ```
4. Press Solve. The result will be **True**, **False**, or **Indeterminate**.

> **Indeterminate** means one or more variables were left unspecified, so the result depends on those free values.

---

## Reading the Results

Each solve produces a trail of expandable cards in order:

| Card | Contents |
|---|---|
| **GIVEN** | The equation as parsed after normalization |
| **METHOD** | Algorithm name, variable count, and equation type code |
| **STEPS** | Numbered derivation steps; each step names the algebraic rule applied |
| **FINAL ANSWER** | The solution, or a special message for tautologies, contradictions, or non-linear input |
| **VERIFICATION** | The answer substituted back into the original equation to confirm correctness |
| **SUMMARY** | Runtime (ms), step count, validation status (PASS / FAIL), timestamp |
| **GRAPH & ANALYSIS** | Matplotlib plot and case classification *(single-variable linear only)* |

Click any card header to expand or collapse it. **Settings → Auto-Expand** opens all cards automatically after each solve.

---

## Symbol Pad

Click the keyboard icon near the input bar to open the symbol pad.

- Clicking a symbol inserts it at the cursor position in the input bar.
- Available symbols include: `÷`, `×`, `√`, `π`, `²`, `³`, and common operators.
- Both the symbol form (`√`, `π`) and the text form (`sqrt`, `pi`) are accepted by the solver.

---

## Sidebar and History

Every solve is saved automatically. Open the sidebar with the **☰** icon at the top left.

**Actions:**

| Action | Description |
|---|---|
| Click entry | Reload that solve in the main results area |
| Pin | Keep the entry at the top of the list |
| Archive | Hide from the main list but keep in history |
| Delete | Remove permanently |
| Search bar | Filter entries by equation text |

History is capped at **200 entries** and persists between sessions in `data/dualsolver.json`.

---

## Export

After a solve completes, export buttons appear below the trail.

| Button | Output |
|---|---|
| **Copy to Clipboard** | Full trail as plain text — paste into any editor or document |
| **Save as HTML** | Self-contained HTML file — open in any browser |
| **Save as PDF** | Formatted PDF with embedded graph and Result Interpretation block |

All exports include every section: equation, method, steps, answer, verification, and summary.

---

## Settings

Open Settings from the sidebar menu or the gear icon.

| Setting | Options | Description |
|---|---|---|
| **Theme** | Six palettes | Switch color palette (Ocean Blue, Obsidian Black, Emerald Green, Sunset Orange, Crimson Red, Violet) |
| **Animation Speed** | Slow / Normal / Fast / Off | Controls how fast step cards animate in |
| **Auto-Expand** | On / Off | When on, all result cards open automatically after solving |

Settings persist between sessions.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Parse error` on a valid-looking equation | Ensure there is exactly one `=`; check for stray operators or unbalanced parentheses |
| App treats `x^2 + 1 = 0` as an error | Intentional — non-linear inputs return an educational explanation, not a solution |
| `Save as PDF` fails with a missing-module error | Run `pip install -r requirements.txt`; requires `fpdf2 >= 2.8` |
| Header shows a text label instead of a logo | Install Pillow: `pip install pillow` |
| Pasting `２ｘ ＝ ４` gives "Invalid character" | Update to v1.0+ — full-width characters are normalized automatically |
| Settings reset after a crash | `data/dualsolver.json` was corrupted and rebuilt from defaults; previous results can be re-exported from memory |
| Substitution returns Indeterminate | One or more variables in the equation were not given a value — provide values for all variables |
