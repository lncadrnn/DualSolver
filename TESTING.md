# DualSolver — Test Plan v1

**Application:** DualSolver v1.0.0
**Date:** April 9, 2026
**Author:** QA Team
**Status:** Active

---

## Table of Contents

1. [What Is This Document?](#1-what-is-this-document)
2. [What Does DualSolver Do?](#2-what-does-dualsolver-do)
3. [How Testing Is Organized](#3-how-testing-is-organized)
4. [Test Categories](#4-test-categories)
   - 4.1 [Solver Tests — Does the Math Work?](#41-solver-tests--does-the-math-work)
   - 4.2 [Numerical Solver Tests — Decimal Answers](#42-numerical-solver-tests--decimal-answers)
   - 4.3 [Graph & Analysis Tests — Are Charts Correct?](#43-graph--analysis-tests--are-charts-correct)
   - 4.4 [History & Storage Tests — Is My Data Saved?](#44-history--storage-tests--is-my-data-saved)
   - 4.5 [Theme Tests — Do Colors Switch Properly?](#45-theme-tests--do-colors-switch-properly)
   - 4.6 [App & Startup Tests — Does the App Open and Respond?](#46-app--startup-tests--does-the-app-open-and-respond)
5. [Manual Testing Checklist](#5-manual-testing-checklist)
   - 5.1 [Basic Workflow](#51-basic-workflow)
   - 5.2 [Computation Modes](#52-computation-modes)
   - 5.3 [Error Handling](#53-error-handling)
   - 5.4 [History Sidebar](#54-history-sidebar)
   - 5.5 [Export & Sharing](#55-export--sharing)
   - 5.6 [Settings & Preferences](#56-settings--preferences)
   - 5.7 [Visual & Accessibility](#57-visual--accessibility)
6. [What Counts as a Pass or Fail](#6-what-counts-as-a-pass-or-fail)
7. [How to Run the Automated Tests](#7-how-to-run-the-automated-tests)
8. [Known Limitations](#8-known-limitations)
9. [Glossary](#9-glossary)

---

## 1. What Is This Document?

This test plan describes **every check we perform** to make sure DualSolver works correctly before it is delivered. It is written so that anyone — developer, instructor, or student — can understand what is being tested and why.

Each section explains:

- **What** we are testing (in plain language).
- **Why** it matters to the user.
- **How** we verify it (automated code tests + manual walkthroughs).

---

## 2. What Does DualSolver Do?

DualSolver is a desktop learning tool that solves **linear equations** step by step. You type an equation (like `2x + 2 = 5`), pick a computation method, and the app shows you:

| Feature                | What It Means                                                                      |
| ---------------------- | ---------------------------------------------------------------------------------- |
| **Symbolic mode**      | Gives exact answers using fractions and symbols (powered by SymPy).                |
| **Numerical mode**     | Gives decimal answers (powered by NumPy).                                          |
| **Substitution mode**  | Lets you plug in values to check if they satisfy the equation.                     |
| **Step-by-step trail** | Every solve shows: Given → Method → Steps → Final Answer → Verification → Summary. |
| **Graph & analysis**   | A chart visualizing the equation and its solution.                                 |
| **History sidebar**    | Saves past solves locally so you can review, pin, archive, or delete them.         |
| **Export**             | Copy the solution to your clipboard or save it as a PDF.                           |
| **Dark / Light theme** | Switch the app's appearance to your preference.                                    |

---

## 3. How Testing Is Organized

We use two layers of testing:

| Layer                              | Who Runs It                                                                  | What It Covers                                                                         |
| ---------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Automated tests** (53 tests)     | A developer types one command and the computer checks everything in seconds. | Math accuracy, data validation, error handling, storage, themes, graph generation.     |
| **Manual tests** (checklist below) | A person opens the app and walks through each scenario by hand.              | Visual appearance, animations, user experience, PDF output, clipboard, responsiveness. |

**Automated tests give us speed.** They run in under a minute and catch regressions immediately.
**Manual tests give us confidence.** They verify what the user actually sees and feels.

---

## 4. Test Categories

### 4.1 Solver Tests — Does the Math Work?

> **File:** `tests/test_engine_unit.py` (13 tests)

These tests verify that the core symbolic solver produces correct, complete results.

| #   | Test Name (plain language)         | What It Checks                                                             | Example                                                                                             |
| --- | ---------------------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| 1   | **Variable detection**             | The solver finds all variables in an equation.                             | `3x + 2 = 7` → detects `x`                                                                          |
| 2   | **Implicit multiplication**        | Expressions like `as + in` are expanded to `a*s + i*n`.                    | Prevents misinterpretation of letter combinations                                                   |
| 3   | **Equation formatting**            | Raw input is prettified for display.                                       | `3x+2=7` → `3x + 2 = 7`                                                                             |
| 4   | **Expression parsing**             | Math text is converted to a computer-readable form.                        | `"2x + 1"` → SymPy object `2*x + 1`                                                                 |
| 5   | **Superscript & fraction display** | Exponents and fractions render with special characters.                    | `1/2` → `⟦1\|2⟧`                                                                                    |
| 6   | **Degree detection**               | Identifies quadratic, cubic, etc.                                          | Degree 2 → "quadratic"                                                                              |
| 7   | **Non-linear detection**           | Recognizes equations the solver cannot handle and explains why.            | `x² + 1 = 0` → educational message                                                                  |
| 8   | **Term counting**                  | Counts additive terms to detect auto-simplification.                       | `2x + 5x + 3` → 3 terms                                                                             |
| 9   | **Character validation**           | Rejects equations with illegal characters.                                 | `2x @ 1 = 0` → error                                                                                |
| 10  | **Complete trail output**          | A valid solve returns all 7 required fields with correct types and ranges. | `2x + 2 = 5` → trail with equation, given, method, steps, final_answer, verification_steps, summary |
| 11  | **Non-linear validation status**   | Non-linear equations log `validation_status = "fail"`.                     | `x^2 + 1 = 0` → fail                                                                                |
| 12  | **System of equations**            | Solves multiple equations simultaneously.                                  | `x + y = 10, x - y = 2` → `x = 6, y = 4`                                                            |
| 13  | **Missing `=` sign**               | Rejects input without an equals sign.                                      | `2x + 3` → error                                                                                    |
| 14  | **Multiple `=` signs**             | Rejects `x = 1 = 2`.                                                       | Error: "exactly one '='"                                                                            |
| 15  | **Bad characters**                 | Rejects `3x + 2 = 7$`.                                                     | Error: "Invalid character"                                                                          |

**Why it matters:** If the math is wrong, nothing else matters. These tests are the foundation.

---

### 4.2 Numerical Solver Tests — Decimal Answers

> **File:** `tests/test_numerical_unit.py` (16 tests)

These tests verify the NumPy-based decimal solver and the mode dispatcher.

| #   | Test Name (plain language)             | What It Checks                                            |
| --- | -------------------------------------- | --------------------------------------------------------- |
| 1   | **Number formatting — integer**        | `7.0` displays as `7` (no unnecessary decimal).           |
| 2   | **Number formatting — clean decimal**  | `2.5` stays as `2.5`.                                     |
| 3   | **Number formatting — trailing zeros** | `1.50000` becomes `1.5`.                                  |
| 4   | **Number formatting — tiny rounding**  | `3.0000000000001` rounds to `3`.                          |
| 5   | **Basic numeric solve**                | `2x + 3 = 7` → `x = 2`.                                   |
| 6   | **Fractional result**                  | `3x + 1 = 2` → `x ≈ 0.3333`.                              |
| 7   | **Negative result**                    | `x + 10 = 3` → `x = -7`.                                  |
| 8   | **Required fields present**            | Numeric results contain all 7 trail fields.               |
| 9   | **Summary fields valid**               | Runtime ≥ 0, library says "NumPy", status is "pass".      |
| 10  | **System solve (2 equations)**         | `x + y = 10, x - y = 2` → `x = 6, y = 4`.                 |
| 11  | **System verification present**        | Verification steps exist after solving a system.          |
| 12  | **Matrix step shown**                  | Solution trail includes a matrix/coefficient step.        |
| 13  | **Quadratic rejected**                 | `x^2 + 1 = 0` triggers educational feedback, not a crash. |
| 14  | **Transcendental rejected**            | `sin(x) = 0` triggers educational feedback.               |
| 15  | **Multi-variable (single eq)**         | `2x + 4y = 1` returns a parametric answer.                |
| 16  | **Invalid input rejected**             | `2x + 3` (no `=`) raises an error.                        |

**Dispatcher tests** (also in this file):

| #   | What It Checks                                                 |
| --- | -------------------------------------------------------------- |
| 17  | Default mode uses SymPy (symbolic).                            |
| 18  | Explicit `mode="symbolic"` uses SymPy.                         |
| 19  | `mode="numerical"` uses NumPy.                                 |
| 20  | Both modes produce the same final answer for a given equation. |
| 21  | System of equations works in both modes.                       |

**Why it matters:** Users who prefer decimal answers need them to be accurate and well-formatted.

---

### 4.3 Graph & Analysis Tests — Are Charts Correct?

> **File:** `tests/test_graph_unit.py` (6 test functions covering 15+ checks)

| #   | Test Name (plain language)   | What It Checks                                                                                  |
| --- | ---------------------------- | ----------------------------------------------------------------------------------------------- |
| 1   | **Theme switching**          | `set_theme("light")` changes graph colors to the light palette.                                 |
| 2   | **Text-only figure**         | A fallback figure with a title and message renders without errors.                              |
| 3   | **Equation parsing**         | `2x + 1 = 5` splits into left side, right side, and variable.                                   |
| 4   | **Invalid equation parsing** | `2x + 1` (no `=`) is rejected.                                                                  |
| 5   | **Single-variable analysis** | Detects "one solution" for `2x + 2 = 5`.                                                        |
| 6   | **Two-variable analysis**    | Correctly identifies `2x + y = 6` as a two-variable problem.                                    |
| 7   | **System analysis**          | Recognizes `x + y = 10, x - y = 2` as a system with one solution.                               |
| 8   | **Symbol prettification**    | `sqrt(x)` → `√(x)`, `pi` → `π` in analysis text.                                                |
| 9   | **Dispatch routing**         | `analyze_result()` picks the right analysis based on equation type.                             |
| 10  | **Figure generation**        | `build_figure()` returns a valid Matplotlib figure for any supported input.                     |
| 11  | **Restyle after build**      | Changing the theme after building a figure does not crash.                                      |
| 12  | **Direct builders**          | Individual chart builders (single-var, two-var, multi-var, system) each produce a valid figure. |

**Why it matters:** Charts help students visualize equations. Broken charts break understanding.

---

### 4.4 History & Storage Tests — Is My Data Saved?

> **File:** `tests/test_storage_unit.py` (8 tests)

| #   | Test Name (plain language)  | What It Checks                                                                          |
| --- | --------------------------- | --------------------------------------------------------------------------------------- |
| 1   | **Save & load settings**    | Changing theme to "light" persists and reloads correctly.                               |
| 2   | **Add & retrieve history**  | Solved equations appear in the history list.                                            |
| 3   | **History limit (200 max)** | Adding 205 entries trims the list to the 200 most recent.                               |
| 4   | **Clear history**           | "Clear All" removes every history entry.                                                |
| 5   | **Pin / unpin**             | Pinning a solve keeps it at the top; unpinning reverses it.                             |
| 6   | **Archive / unarchive**     | Archived items disappear from the default view but can be retrieved.                    |
| 7   | **Delete single item**      | Deleting one entry leaves the rest intact.                                              |
| 8   | **Clear all data**          | Resets both settings and history to defaults.                                           |
| 9   | **Corrupt file recovery**   | If the data file is corrupted (invalid JSON), the app starts fresh instead of crashing. |
| 10  | **File persistence**        | Data written to disk can be read back correctly.                                        |
| 11  | **Old format migration**    | Legacy data formats are automatically converted to the current format.                  |

**Why it matters:** Losing saved work is frustrating. These tests ensure data is reliable.

---

### 4.5 Theme Tests — Do Colors Switch Properly?

> **File:** `tests/test_themes_unit.py` (2 tests)

| #   | Test Name (plain language) | What It Checks                                                                                     |
| --- | -------------------------- | -------------------------------------------------------------------------------------------------- |
| 1   | **Palette lookup**         | `palette("dark")` returns the dark color set; `palette("light")` returns the light set.            |
| 2   | **Apply theme**            | Switching to "light" updates all color variables app-wide; switching back to "dark" restores them. |

**Why it matters:** A theme that half-switches leaves the app looking broken.

---

### 4.6 App & Startup Tests — Does the App Open and Respond?

> **File:** `tests/test_app_and_main_unit.py` (3 tests)

| #   | Test Name (plain language)      | What It Checks                                                                                                                         |
| --- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Friendly error messages**     | A parse error shows "Could not understand…" instead of a cryptic traceback. A generic error shows "could not process… Details: …"      |
| 2   | **Error display without crash** | When the app shows an error: the loading spinner is removed, the input field is re-enabled, and focus returns to the input — no crash. |
| 3   | **App launches**                | Running `main.py` creates the app and calls `mainloop()` (the window opens).                                                           |

**Why it matters:** First impressions count. If the app crashes on startup or shows scary error messages, users lose trust.

---

## 5. Manual Testing Checklist

Use this checklist when testing the app by hand. Mark each row **Pass** or **Fail**.

### 5.1 Basic Workflow

| #   | Step                                                 | Expected Result                                                                                       | Pass / Fail |
| --- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ----------- |
| M-1 | Open the app (`python main.py`).                     | The window appears with a chat area, input bar, and sidebar.                                          |             |
| M-2 | Type `2x + 2 = 5` and press Enter.                   | A mode selection dialog appears (Symbolic / Numerical / Substitution).                                |             |
| M-3 | Choose **Symbolic**.                                 | The trail appears: Given → Method → Steps → Final Answer → Verification → Summary. Answer: `x = 3/2`. |             |
| M-4 | Choose **Numerical** for the same equation.          | Trail appears with answer: `x = 1.5`. Library shows "NumPy".                                          |             |
| M-5 | Type `x + y = 10, x - y = 2` and solve symbolically. | Answer shows `x = 6` and `y = 4`.                                                                     |             |
| M-6 | Scroll through the trail cards.                      | Each card expands/collapses smoothly. Text is readable.                                               |             |

### 5.2 Computation Modes

| #    | Step                                                | Expected Result                                   | Pass / Fail |
| ---- | --------------------------------------------------- | ------------------------------------------------- | ----------- |
| M-7  | Solve `3x + 1 = 2` in **Symbolic** mode.            | Answer: `x = 1/3` (fraction).                     |             |
| M-8  | Solve `3x + 1 = 2` in **Numerical** mode.           | Answer: `x = 0.3333…` (decimal).                  |             |
| M-9  | Solve `x + 1 = 3` in **Substitution** with `x = 2`. | Verification confirms the equation is satisfied.  |             |
| M-10 | Solve `x + 1 = 3` in **Substitution** with `x = 5`. | Verification shows the equation is NOT satisfied. |             |

### 5.3 Error Handling

| #    | Step                                    | Expected Result                                                                                | Pass / Fail |
| ---- | --------------------------------------- | ---------------------------------------------------------------------------------------------- | ----------- |
| M-11 | Type `2x + 3` (no `=`) and press Enter. | A clear error message appears: "must contain '='". The app does not crash. Input stays usable. |             |
| M-12 | Type `x = 1 = 2` and press Enter.       | Error: "exactly one '='". No crash.                                                            |             |
| M-13 | Type `3x + 2 = 7$` and press Enter.     | Error: "Invalid character". No crash.                                                          |             |
| M-14 | Type `x^2 + 1 = 0` and solve.           | An educational message explains this is non-linear (quadratic), not a crash or wrong answer.   |             |
| M-15 | Type `sin(x) = 0` and solve.            | Educational message about transcendental equations.                                            |             |
| M-16 | Submit an empty input.                  | Nothing happens or a gentle prompt appears. No crash.                                          |             |

### 5.4 History Sidebar

| #    | Step                           | Expected Result                                               | Pass / Fail |
| ---- | ------------------------------ | ------------------------------------------------------------- | ----------- |
| M-17 | Solve two different equations. | Both appear in the sidebar, most recent first.                |             |
| M-18 | Pin the first entry.           | The pinned entry has a visual indicator and stays at the top. |             |
| M-19 | Archive the second entry.      | It disappears from the default sidebar view.                  |             |
| M-20 | View archived entries.         | The archived entry is visible in the archive view.            |             |
| M-21 | Delete a history entry.        | It is removed permanently. Other entries remain.              |             |
| M-22 | Click "Clear History".         | All entries are removed.                                      |             |
| M-23 | Close and reopen the app.      | Previous history is still there (data persists).              |             |

### 5.5 Export & Sharing

| #    | Step                                                 | Expected Result                                                               | Pass / Fail |
| ---- | ---------------------------------------------------- | ----------------------------------------------------------------------------- | ----------- |
| M-24 | Solve an equation, then click **Copy to Clipboard**. | Paste into a text editor — the full trail text appears correctly.             |             |
| M-25 | Click **Save as PDF**.                               | A PDF file is created. Open it — the trail is legible with proper formatting. |             |

### 5.6 Settings & Preferences

| #    | Step                                         | Expected Result                                                        | Pass / Fail |
| ---- | -------------------------------------------- | ---------------------------------------------------------------------- | ----------- |
| M-26 | Open Settings and switch to **Light** theme. | The entire app (chat, sidebar, input, cards) switches to light colors. |             |
| M-27 | Switch back to **Dark** theme.               | Everything returns to dark colors.                                     |             |
| M-28 | Change **animation speed**.                  | Trail card animations speed up or slow down accordingly.               |             |
| M-29 | Toggle section auto-expand.                  | Sections either expand automatically or stay collapsed as configured.  |             |
| M-30 | Close and reopen the app.                    | Settings persist (theme, speed, preferences).                          |             |

### 5.7 Visual & Accessibility

| #    | Step                                             | Expected Result                                                              | Pass / Fail |
| ---- | ------------------------------------------------ | ---------------------------------------------------------------------------- | ----------- |
| M-31 | Resize the window.                               | The layout adapts. No elements are cut off or overlap.                       |             |
| M-32 | Check the Graph & Analysis panel.                | The chart displays correctly with labeled axes and a visible solution point. |             |
| M-33 | Open the About / Help page (`?` button).         | The help page opens with clear usage instructions.                           |             |
| M-34 | Use the symbol pad to insert `≤`, `≥`, `π`, etc. | Symbols are inserted into the input field at the cursor position.            |             |
| M-35 | Verify solid color interface rendering.           | Panels and window backgrounds render as opaque solid colors with no blur.     |             |

---

## 6. What Counts as a Pass or Fail

| Outcome     | Meaning                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------- |
| **Pass**    | The test produces the expected result with no errors, crashes, or visual defects.                       |
| **Fail**    | The result is wrong, the app crashes, an error message is missing or unclear, or the display is broken. |
| **Blocked** | The test cannot run due to an environment issue (e.g., missing dependency).                             |

**Severity guide for failures:**

| Severity     | Definition                                       | Example                                            |
| ------------ | ------------------------------------------------ | -------------------------------------------------- |
| **Critical** | The app crashes or produces a wrong math answer. | `2x + 2 = 5` returns `x = 2` instead of `x = 3/2`. |
| **High**     | A feature does not work but the app stays open.  | Export to PDF produces a blank file.               |
| **Medium**   | Cosmetic or minor functional issue.              | Theme switch leaves one panel in the old color.    |
| **Low**      | Minor visual inconsistency.                      | A button is 2 pixels misaligned.                   |

---

## 7. How to Run the Automated Tests

### Prerequisites

1. Python 3.10 or higher installed.
2. Virtual environment activated.
3. All dependencies installed (`pip install -r requirements.txt`).

### Run all 53 tests

```bash
pytest
```

### Run with verbose output (shows each test name)

```bash
pytest -v
```

### Run a specific test file

```bash
pytest tests/test_engine_unit.py
pytest tests/test_numerical_unit.py
pytest tests/test_graph_unit.py
pytest tests/test_storage_unit.py
pytest tests/test_themes_unit.py
pytest tests/test_app_and_main_unit.py
```

### Run a single test by name

```bash
pytest -k "test_solve_linear_equation_required_fields"
```

### What success looks like

```
========================= 53 passed in X.XXs =========================
```

All 53 tests should show **passed** with zero failures or errors.

---

## 8. Known Limitations

| Area               | Limitation                                                                                                                                   |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Equation types** | Only linear equations are fully solved. Non-linear inputs (quadratic, trigonometric, etc.) receive educational feedback but are not solved.  |
| **Visual style**   | The interface uses opaque solid-color panels by design (no OS blur effects).                                                   |
| **Logo display**   | The app logo requires the `Pillow` library. Without it, a text label is shown instead.                                                       |
| **Offline only**   | All data is stored locally in `data/dualsolver.json`. There is no cloud sync or multi-device support.                                        |
| **History cap**    | A maximum of 200 history entries are kept. Older entries are automatically removed.                                                          |

---

## 9. Glossary

| Term                    | Meaning                                                                                                                                          |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Linear equation**     | An equation where variables appear only to the first power (e.g., `2x + 3 = 7`). No squares, cubes, or trigonometry.                             |
| **Symbolic solving**    | Finding the exact answer using algebra (fractions, symbols). Powered by SymPy.                                                                   |
| **Numerical solving**   | Finding an approximate decimal answer. Powered by NumPy.                                                                                         |
| **Substitution**        | Plugging a specific value into an equation to check if it makes both sides equal.                                                                |
| **Trail**               | The step-by-step solution walkthrough: Given → Method → Steps → Final Answer → Verification → Summary.                                           |
| **Validation status**   | A pass/fail label in the trail summary indicating whether the solver verified its own answer.                                                    |
| **System of equations** | Two or more equations solved together (e.g., `x + y = 10, x - y = 2`).                                                                           |
| **Non-linear**          | An equation involving powers, roots, or trig functions (e.g., `x² + 1 = 0`). DualSolver detects these and explains them but does not solve them. |
| **Solid theme**         | An opaque interface style where panels and cards use fixed colors instead of translucency or blur.                                             |
| **SymPy**               | A Python library for symbolic mathematics.                                                                                                       |
| **NumPy**               | A Python library for numerical computation.                                                                                                      |
| **Matplotlib**          | A Python library for creating charts and graphs.                                                                                                 |
| **pytest**              | The testing framework used to run automated tests.                                                                                               |
