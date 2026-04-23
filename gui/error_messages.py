"""Educational user-facing error messages for solver failures.

This module centralizes all hardcoded, explanatory error text so the GUI
can keep presentation logic separate from message datasets.
"""


def format_educational_error(equation: str, exc: Exception) -> str:
    """Return an educational message for a solver exception."""
    msg = str(exc).strip()
    msg_l = msg.lower()
    entered = equation.strip() or equation

    if "invalid character(s):" in msg_l:
        if any(sym in msg for sym in ("<", ">", "≤", "≥")):
            return (
                "This input uses an inequality symbol, not an equation symbol.\n\n"
                f'You entered: "{entered}"\n\n'
                "DualSolver solves equations, which must use '=' to compare\n"
                "left and right sides. Symbols like <, >, ≤, and ≥ are\n"
                "inequalities and are outside the current solver scope.\n\n"
                "How to fix it:\n"
                "- Replace inequality symbols with '=' when appropriate.\n"
                "- Keep exactly one '=' per equation.\n"
                "- Example: 2x + 3 = 7"
            )
        return (
            "Some characters in your input are not valid math symbols.\n\n"
            f'You entered: "{entered}"\n\n'
            "DualSolver accepts letters, numbers, spaces, and math symbols.\n"
            "Allowed symbols: +  -  *  /  ^  =  ( )  .  ,  ;\n\n"
            "How to fix it:\n"
            "- Remove unsupported characters (for example: $, @, #).\n"
            "- Keep only equation text and allowed math symbols.\n"
            "- Example: 2x + 3 = 7"
        )

    if "each equation must contain '=" in msg_l:
        problem = msg.split("Problem:", 1)[1].strip() if "Problem:" in msg else ""
        detail = f'Problem part: "{problem}"\n\n' if problem else ""
        return (
            "A system of equations needs '=' in every equation part.\n\n"
            f'You entered: "{entered}"\n\n'
            f"{detail}"
            "When you separate equations with commas or semicolons,\n"
            "each piece must be a full equation.\n\n"
            "How to fix it:\n"
            "- Write each part as left_side = right_side.\n"
            "- Example: x + y = 10, x - y = 2"
        )

    if "each equation must have exactly one '=" in msg_l:
        problem = msg.split("Problem:", 1)[1].strip() if "Problem:" in msg else ""
        detail = f'Problem part: "{problem}"\n\n' if problem else ""
        return (
            "Each equation in a system must have one and only one '=' sign.\n\n"
            f'You entered: "{entered}"\n\n'
            f"{detail}"
            "If one part has no '=', or has multiple '=', parsing becomes ambiguous.\n\n"
            "How to fix it:\n"
            "- Keep exactly one '=' per equation.\n"
            "- Example: x + y = 10, x - y = 2"
        )

    if "must contain '=" in msg_l and "equation" in msg_l:
        return (
            "What you entered is an expression, not an equation yet.\n\n"
            f'You entered: "{entered}"\n\n'
            "For it to become an equation, it must equate one side to another.\n"
            "A linear equation compares two sides using '='.\n"
            "Without '=', there is no equality relationship to solve.\n\n"
            "How to fix it:\n"
            "- Add exactly one '=' sign.\n"
            "- Put an expression on both sides of '='.\n"
            "- If one side is blank, complete it (for example: x + 2 = 5).\n"
            "- Example: 2x + 3 = 7"
        )

    if "exactly one '=' sign" in msg_l or "exactly one '=" in msg_l:
        return (
            "Your input should contain exactly one '=' sign per equation.\n\n"
            f'You entered: "{entered}"\n\n'
            "Using more than one '=' in one equation creates a chain that\n"
            "the linear solver cannot interpret as a single equation.\n\n"
            "How to fix it:\n"
            "- Rewrite as one left side and one right side.\n"
            "- Example: x + 2 = 5"
        )

    if "both sides of the equation must have expressions" in msg_l:
        return (
            "Both sides of '=' need math expressions.\n\n"
            f'You entered: "{entered}"\n\n'
            "An equation is incomplete if one side is blank\n"
            "(for example: 'x + 2 =' or '= 5').\n\n"
            "How to fix it:\n"
            "- Add a valid expression on the left and right sides.\n"
            "- Example: x + 2 = 5"
        )

    if "no variable found" in msg_l:
        return (
            "A solvable linear equation needs at least one variable letter.\n\n"
            f'You entered: "{entered}"\n\n'
            "Numbers alone are constants, not unknowns to solve for.\n"
            "A constants-only statement may be true or false, but it does not\n"
            "ask for a variable value.\n\n"
            "How to fix it:\n"
            "- Include a variable like x, y, or z.\n"
            "- Example: 2x + 3 = 7"
        )

    if "missing value(s) for variable(s):" in msg_l:
        return (
            "Substitution mode needs a value for every variable in the equation.\n\n"
            f'You entered equation: "{entered}"\n\n'
            f"Details from solver: {msg}\n\n"
            "How to fix it:\n"
            "- Provide assignments for all variables found in the equation.\n"
            "- Example equation: x + y = 10\n"
            "- Example values: x = 4, y = 6"
        )

    if "no values provided" in msg_l:
        return (
            "Substitution mode is a check with given values, so values are required.\n\n"
            f'You entered equation: "{entered}"\n\n'
            "How to fix it:\n"
            "- Enter at least one variable assignment.\n"
            "- Example: x = 3\n"
            "- For multiple variables: x = 3, y = 4"
        )

    if "invalid value format:" in msg_l:
        return (
            "A substitution value is formatted incorrectly.\n\n"
            f'You entered equation: "{entered}"\n\n'
            f"Details from solver: {msg}\n\n"
            "How to fix it:\n"
            "- Use variable = value format.\n"
            "- Separate multiple assignments with commas.\n"
            "- Example: x = 3, y = 4"
        )

    if "variable name must be a single letter" in msg_l:
        return (
            "Substitution variable names must be single letters.\n\n"
            f'You entered equation: "{entered}"\n\n'
            f"Details from solver: {msg}\n\n"
            "How to fix it:\n"
            "- Use names like x, y, z in the values input.\n"
            "- Example: x = 3, y = 4"
        )

    if "could not parse value for" in msg_l:
        return (
            "One of the substitution values could not be read as math.\n\n"
            f'You entered equation: "{entered}"\n\n'
            f"Details from solver: {msg}\n\n"
            "How to fix it:\n"
            "- Check each value expression for valid math syntax.\n"
            "- Use operators like +, -, *, /, ^ and balanced parentheses.\n"
            "- Example: x = 3/2, y = sqrt(9)"
        )

    if "could not parse expression" in msg_l or "invalid syntax" in msg_l:
        if any(key in msg_l for key in (
            "eof", "never closed", "unmatched", "parenthesis", "expected ')'"
        )):
            return (
                "The equation syntax looks incomplete because parentheses are not balanced.\n\n"
                f'You entered: "{entered}"\n\n'
                "How to fix it:\n"
                "- Make sure every opening '(' has a closing ')'.\n"
                "- Complete any unfinished term before or after parentheses.\n"
                "- Example: 2(x + 3) = 14"
            )
        return (
            "Part of the equation could not be parsed as valid math syntax.\n\n"
            f'You entered: "{entered}"\n\n'
            "This often happens with missing operators, unclosed parentheses,\n"
            "or incomplete terms.\n\n"
            "How to fix it:\n"
            "- Check parentheses are balanced.\n"
            "- Remove trailing operators (like '2x +').\n"
            "- Example: 2x + 3 = 7"
        )

    if "could not determine the degree" in msg_l:
        return (
            "DualSolver could not confirm this is a standard linear form.\n\n"
            f'You entered: "{entered}"\n\n'
            "A linear equation has variables only to the first power and\n"
            "can be rearranged into ax + b = c form.\n\n"
            "How to fix it:\n"
            "- Simplify the equation and try again.\n"
            "- Avoid unsupported or ambiguous structure.\n"
            "- Example: 3x - 5 = 10"
        )

    if "could not solve system numerically" in msg_l:
        if "singular matrix" in msg_l:
            return (
                "The numerical system has no unique solution (singular matrix).\n\n"
                f'You entered: "{entered}"\n\n'
                "This usually means at least one equation is a multiple of another\n"
                "(dependent system) or the system is inconsistent.\n\n"
                "How to fix it:\n"
                "- Check whether equations are duplicates or scalar multiples.\n"
                "- Add or correct equations so each adds independent information.\n"
                "- Try symbolic mode to see whether solutions are infinite or none.\n"
                "- Example independent system: x + y = 10, x - y = 2"
            )
        return (
            "The numerical solver could not compute this system as entered.\n\n"
            f'You entered: "{entered}"\n\n'
            "This can happen when equations are inconsistent, dependent,\n"
            "or numerically unstable in matrix form.\n\n"
            "How to fix it:\n"
            "- Check each equation for typos.\n"
            "- Try symbolic mode for a structural explanation.\n"
            "- Example system: x + y = 10, x - y = 2"
        )

    if isinstance(exc, ValueError):
        return (
            "Your equation input is not in a supported linear format yet.\n\n"
            f'You entered: "{entered}"\n\n'
            "How to fix it:\n"
            "- Use one equation with exactly one '=' sign, or\n"
            "  a system separated by commas/semicolons.\n"
            "- Keep expressions linear (no x^2, no x in denominator).\n"
            "- Example: 2x + 3 = 7\n"
            "- Example system: x + y = 10, x - y = 2\n\n"
            f"Details from solver: {msg}"
        )

    return (
        "DualSolver hit an unexpected problem while solving this input.\n\n"
        f'You entered: "{entered}"\n\n'
        "How to continue:\n"
        "- Recheck the equation format and try again.\n"
        "- If the same input keeps failing, try a simpler equivalent form.\n"
        "- Example: 2x + 3 = 7\n\n"
        f"Technical detail: {msg}"
    )
