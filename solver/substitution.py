"""Substitution (verification) solver for DualSolver.

Given an equation like ``2x + 1 = 7`` and user-supplied values like
``x = 3``, this module substitutes the values into the equation and
checks whether the equation holds true — producing step-by-step
explanations along the way.
"""

import re
import time
from datetime import datetime

import sympy
from sympy import symbols, sympify, simplify, expand, Symbol, Eq
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application,
    convert_xor, rationalize,
)

from solver.symbolic import (
    TRANSFORMATIONS,
    _detect_variables,
    _expand_implicit_vars,
    _parse_side,
    _format_expr,
    _format_expr_plain,
    _format_input_str,
    _format_input_eq,
    _format_equation,
    _prettify_symbols,
    _normalize_spacing,
    _validate_characters,
    _validate_equation_structure,
    _validate_input_length,
    _normalize_unicode,
    _FRAC_OPEN,
    _frac,
    # Algebraic-property labels (shared with symbolic.py for trail consistency)
    _PROP_GIVEN,
    _PROP_SUBSTITUTION,
    _PROP_SIMPLIFY,
    _PROP_DEFINITION,
    _PROP_IDENTITY,
    _PROP_CONTRADICTION,
)


def _strip_trailing_zeros(s: str) -> str:
    """Remove unnecessary trailing zeros from decimal strings.

    ``'7.0000000000000'`` → ``'7'``
    ``'7.21310000000'``  → ``'7.2131'``
    ``'-3.85840734641021'`` stays as-is (no trailing zeros).
    """
    if '.' not in s:
        return s
    # Handle negative sign separately
    parts = s.split()
    cleaned = []
    for part in parts:
        if '.' in part:
            part = part.rstrip('0').rstrip('.')
        cleaned.append(part)
    return ' '.join(cleaned)


def _parse_values(values_str: str) -> dict[str, str]:
    """Parse a user-supplied values string like ``x = 3, y = 4``.

    Returns a dict mapping variable names to their raw value strings.
    """
    assignments = re.split(r'\s*[,;]\s*', values_str.strip())
    result = {}
    for assignment in assignments:
        assignment = assignment.strip()
        if not assignment:
            continue
        if '=' not in assignment:
            raise ValueError(
                f"Invalid value format: '{assignment}'. "
                f"Expected format: variable = value (e.g. x = 3)"
            )
        parts = assignment.split('=', 1)
        var_name = parts[0].strip()
        val_str = parts[1].strip()
        if not var_name or not val_str:
            raise ValueError(
                f"Invalid value format: '{assignment}'. "
                f"Both variable name and value are required."
            )
        if len(var_name) != 1 or not var_name.isalpha():
            raise ValueError(
                f"Variable name must be a single letter, got '{var_name}'."
            )
        result[var_name] = val_str
    if not result:
        raise ValueError(
            "No values provided. Enter values like: x = 3  or  x = 3, y = 4"
        )
    return result


def solve_substitution(equation_str: str, values_str: str,
                       compute_mode: str = "symbolic") -> dict:
    """Substitute user-given values into an equation and verify.

    Parameters
    ----------
    equation_str : str
        The equation to check (e.g. ``2x + 1 = 7``).
    values_str : str
        Comma-separated variable assignments (e.g. ``x = 3``).
    compute_mode : str, optional
        ``"symbolic"`` (default) — exact results (fractions, π, etc.).
        ``"numerical"`` — decimal approximations.

    Returns
    -------
    dict
        Trail-format result with given, method, steps, final_answer,
        verification_steps, and summary.
    """
    t_start = time.perf_counter()

    # ── Validate input length ────────────────────────────────────────
    _validate_input_length(equation_str)

    # ── Normalise look-alike / full-width Unicode to ASCII ───────────
    equation_str = _normalize_unicode(equation_str)
    values_str = _normalize_unicode(values_str)

    # ── Normalise Unicode ────────────────────────────────────────────
    equation_str = equation_str.replace('\u221a', 'sqrt')
    equation_str = equation_str.replace('\u03c0', '(pi)')
    equation_str = equation_str.replace('[', '(').replace(']', ')')
    equation_str = equation_str.replace('{', '(').replace('}', ')')

    values_str = values_str.replace('\u03c0', '(pi)')

    # ── Validate ─────────────────────────────────────────────────────
    _validate_characters(equation_str)
    _validate_equation_structure(equation_str)

    if '=' not in equation_str:
        raise ValueError("Equation must contain '='. Example: 2x + 1 = 7")

    # ── Parse the user-supplied values ───────────────────────────────
    user_values = _parse_values(values_str)

    # ── Detect variables in the equation ─────────────────────────────
    eq_vars = _detect_variables(equation_str)

    # Check that user supplied values for all variables in the equation
    missing = [v for v in eq_vars if v not in user_values]
    if missing:
        raise ValueError(
            f"Missing value(s) for variable(s): {', '.join(missing)}. "
            f"Please provide values for all variables in the equation."
        )

    # ── Split equation ───────────────────────────────────────────────
    eq_parts = equation_str.split('=')
    if len(eq_parts) != 2:
        raise ValueError("Equation must contain exactly one '=' sign.")

    lhs_str = eq_parts[0].strip()
    rhs_str = eq_parts[1].strip()
    if not lhs_str or not rhs_str:
        raise ValueError("Both sides of the equation must have expressions.")

    # ── Create symbols and parse values ──────────────────────────────
    var_symbols = {name: symbols(name) for name in eq_vars}
    sym_list = list(var_symbols.values())

    # Parse each side
    if len(sym_list) == 1:
        lhs_expr = _parse_side(lhs_str, sym_list[0])
        rhs_expr = _parse_side(rhs_str, sym_list[0])
    else:
        lhs_expr = _parse_side(lhs_str, sym_list)
        rhs_expr = _parse_side(rhs_str, sym_list)

    # Parse the user-supplied numeric/symbolic values
    parsed_values = {}
    for var_name, val_str in user_values.items():
        val_str_clean = val_str.replace('^', '**')
        try:
            parsed_val = parse_expr(val_str_clean, transformations=TRANSFORMATIONS)
            parsed_values[var_name] = parsed_val
        except Exception as e:
            raise ValueError(
                f"Could not parse value for {var_name}: '{val_str}'. Error: {e}"
            )

    # ── Format originals for display ─────────────────────────────────
    _fmt_lhs = _format_input_str(lhs_str)
    _fmt_rhs = _format_input_str(rhs_str)
    _fmt_eq = _format_input_eq(lhs_str, rhs_str)

    # Build a readable values string
    values_display_parts = []
    for var_name in sorted(parsed_values):
        val_formatted = _format_expr(parsed_values[var_name])
        values_display_parts.append(f"{var_name} = {val_formatted}")
    values_display = ", ".join(values_display_parts)

    # ── Build steps ──────────────────────────────────────────────────
    steps = []

    # Step 1: Show original equation
    steps.append({
        "description": "Starting with the original equation",
        "expression": _fmt_eq,
        "explanation": (
            f"We are given the equation {_fmt_lhs} = {_fmt_rhs}. "
            f"We need to check whether this equation holds true when "
            f"{values_display}."
        ),
        "property": _PROP_GIVEN,
    })

    # Step 2: State the given values
    steps.append({
        "description": "Given values to substitute",
        "expression": values_display,
        "explanation": (
            f"We will substitute the given value(s) — {values_display} — "
            f"into the equation and evaluate both sides to check if they are equal."
        ),
        "property": _PROP_DEFINITION,
    })

    # Step 3: Show substitution
    lhs_sub_display = _format_expr(lhs_expr)
    rhs_sub_display = _format_expr(rhs_expr)
    for var_name, val in parsed_values.items():
        val_str_display = _format_expr_plain(val)
        lhs_sub_display = lhs_sub_display.replace(var_name, f'({val_str_display})')
        rhs_sub_display = rhs_sub_display.replace(var_name, f'({val_str_display})')

    steps.append({
        "description": f"Substitute {values_display} into the equation",
        "expression": f"{lhs_sub_display} = {rhs_sub_display}",
        "explanation": (
            f"We replace every variable with its given value in the equation."
        ),
        "property": _PROP_SUBSTITUTION,
    })

    # Step 4: Evaluate LHS and RHS — separate steps so students can follow
    # each side's arithmetic independently.
    subs_dict = {var_symbols[name]: val for name, val in parsed_values.items()}
    lhs_result = simplify(lhs_expr.subs(subs_dict))
    rhs_result = simplify(rhs_expr.subs(subs_dict))

    # Convert to decimal if numerical mode
    if compute_mode == "numerical":
        lhs_result = lhs_result.evalf()
        rhs_result = rhs_result.evalf()

    lhs_result_str = _format_expr(lhs_result)
    rhs_result_str = _format_expr(rhs_result)
    lhs_result_plain = _format_expr_plain(lhs_result)
    rhs_result_plain = _format_expr_plain(rhs_result)

    # Strip trailing zeros for numerical mode
    if compute_mode == "numerical":
        lhs_result_str = _strip_trailing_zeros(lhs_result_str)
        rhs_result_str = _strip_trailing_zeros(rhs_result_str)
        lhs_result_plain = _strip_trailing_zeros(lhs_result_plain)
        rhs_result_plain = _strip_trailing_zeros(rhs_result_plain)

    steps.append({
        "description": "Evaluate the left-hand side (LHS)",
        "expression": f"LHS = {lhs_sub_display} = {lhs_result_str}",
        "explanation": (
            f"Compute the left-hand side after substitution: "
            f"{lhs_sub_display} = {lhs_result_plain}."
        ),
        "property": _PROP_SIMPLIFY,
    })

    steps.append({
        "description": "Evaluate the right-hand side (RHS)",
        "expression": f"RHS = {rhs_sub_display} = {rhs_result_str}",
        "explanation": (
            f"Compute the right-hand side after substitution: "
            f"{rhs_sub_display} = {rhs_result_plain}."
        ),
        "property": _PROP_SIMPLIFY,
    })

    # Step 5: Subtract RHS from LHS — this is the "equation value" (signed gap)
    equation_value = simplify(lhs_result - rhs_result)
    if compute_mode == "numerical":
        equation_value = equation_value.evalf()
    eq_val_str = _format_expr(equation_value)
    eq_val_plain = _format_expr_plain(equation_value)

    if compute_mode == "numerical":
        eq_val_str = _strip_trailing_zeros(eq_val_str)
        eq_val_plain = _strip_trailing_zeros(eq_val_plain)

    # Determine outcome — true / false / indeterminate.
    # The substituted expression might still contain free variables (e.g. user
    # supplied a partial substitution for a multi-variable equation); in that
    # case we cannot decide pass/fail purely from the value, so call it
    # indeterminate and surface it clearly.
    _residual_free = (equation_value.free_symbols if hasattr(equation_value, "free_symbols") else set())
    if _residual_free:
        outcome = "indeterminate"
    else:
        outcome = "true" if equation_value == 0 else "false"
    is_valid = (outcome == "true")

    steps.append({
        "description": "Compute the gap (LHS - RHS)",
        "expression": (
            f"{lhs_result_str} - ({rhs_result_str}) = {eq_val_str}"
        ),
        "explanation": (
            f"Subtract the RHS from the LHS. The result, {eq_val_plain}, "
            f"tells us whether the equation holds: a result of 0 means TRUE, "
            f"a non-zero numeric result means FALSE, and a result that still "
            f"contains variables means the outcome depends on those variables."
        ),
        "property": _PROP_SIMPLIFY,
    })

    if outcome == "true":
        validation_status = "pass"
        verdict_prop = _PROP_IDENTITY
        verdict_expr = (
            f"LHS = RHS = {lhs_result_str}   ->  TRUE statement  (OK)"
        )
        verdict_explanation = (
            f"After substitution the equation becomes "
            f"{lhs_result_plain} = {rhs_result_plain}, which is a TRUE "
            f"statement. The given values DO satisfy the equation."
        )
        final_answer = (
            f"{lhs_result_plain} = {rhs_result_plain}\n"
            f"LHS and RHS are equal  ✓\n"
            f"Verdict: TRUE — the values satisfy the equation.\n"
            f"Equation value (LHS - RHS) = {eq_val_str}"
        )
    elif outcome == "false":
        validation_status = "fail"
        verdict_prop = _PROP_CONTRADICTION
        verdict_expr = (
            f"LHS = {lhs_result_str}, RHS = {rhs_result_str}   ->  FALSE statement  (X)"
        )
        verdict_explanation = (
            f"After substitution the equation becomes "
            f"{lhs_result_plain} = {rhs_result_plain}, which is FALSE "
            f"(the two sides are not equal). The given values do NOT "
            f"satisfy the equation."
        )
        final_answer = (
            f"{lhs_result_plain} ≠ {rhs_result_plain}\n"
            f"LHS and RHS are NOT equal  ✗\n"
            f"Verdict: FALSE — the values do not satisfy the equation.\n"
            f"Equation value (LHS - RHS) = {eq_val_str}"
        )
    else:  # indeterminate
        validation_status = "fail"
        verdict_prop = _PROP_DEFINITION
        verdict_expr = (
            f"LHS - RHS = {eq_val_str}   ->  depends on remaining variables"
        )
        verdict_explanation = (
            f"After substitution the equation still contains free variables "
            f"({', '.join(sorted(str(s) for s in _residual_free))}). "
            f"Whether the equation is true depends on what those variables "
            f"are — supply values for all variables for a definitive verdict."
        )
        final_answer = (
            f"INDETERMINATE — the substitution leaves free variables.\n"
            f"LHS - RHS = {eq_val_str} (not a constant).\n"
            f"Supply values for all variables for a definite TRUE / FALSE."
        )

    # Verification step — restate verdict and what it means.  Even though
    # substitution is itself a verification activity, mirroring the
    # symbolic / numerical solvers' shape keeps the trail UI consistent.
    verification_steps = [{
        "step_number": 1,
        "description": "Verify by comparing both sides",
        "expression": verdict_expr,
        "explanation": verdict_explanation,
        "property": verdict_prop,
    }]

    # ── Number the steps ─────────────────────────────────────────────
    for i, step in enumerate(steps, start=1):
        step["step_number"] = i

    # ── Build trail metadata ─────────────────────────────────────────
    t_end = time.perf_counter()
    runtime_ms = round((t_end - t_start) * 1000, 2)

    given = {
        "problem": f"Check equation by substitution: {_fmt_eq}",
        "inputs": {
            "equation":   _fmt_eq,
            "left_side":  _fmt_lhs,
            "right_side": _fmt_rhs,
            "values":     values_display,
            "computation": ("Substitution — Numerical (SymPy)"
                            if compute_mode == "numerical"
                            else "Substitution — Symbolic (SymPy)"),
        },
    }

    method = {
        "name": "Substitution Check",
        "description": (
            "Substitute user-given values into the equation and verify "
            "whether both sides are equal."
        ),
        "parameters": {
            "equation_type": "Substitution Verification",
            "equation_type_code": f"substitution_{outcome}",
            "variables": ", ".join(sorted(parsed_values.keys())),
            "approach": "Substitute → Evaluate LHS → Evaluate RHS → Compare",
        },
    }

    summary = {
        "runtime_ms": runtime_ms,
        "total_steps": len(steps),
        "verification_steps": len(verification_steps),
        "validation_status": validation_status,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "library": (f"NumPy {__import__('numpy').__version__}"
                    if compute_mode == "numerical"
                    else f"SymPy {sympy.__version__}"),
        "python": None,
    }

    return {
        "equation": equation_str,
        "given": given,
        "method": method,
        "steps": steps,
        "final_answer": final_answer,
        "verification_steps": verification_steps,
        "summary": summary,
    }
