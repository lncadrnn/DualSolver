"""Week 8 — Robustness: edge-case tests.

Documented edge cases
─────────────────────
1. Extremely long input (>500 chars)   → ValueError with length message
2. Division by zero in expression      → ValueError, no crash
3. Constant equation (no variables)    → tautology / contradiction trail with warnings
4. Identity equation (x = x)           → degenerate trail with warnings
5. Contradiction equation (x+3 = x+5) → degenerate trail with warnings
6. Large coefficients, numerical mode  → precision warning in trail
7. Deeply nested parentheses           → solves correctly, no crash
"""

import pytest

from solver import engine


# ── Edge Case 1: Extremely long input ────────────────────────────────────

class TestLongInput:
    def test_symbolic_rejects_long_input(self):
        long_eq = "x + " * 200 + "1 = 0"  # >500 chars
        with pytest.raises(ValueError, match="too long"):
            engine.solve_linear_equation(long_eq)

    def test_numerical_rejects_long_input(self):
        long_eq = "x + " * 200 + "1 = 0"
        with pytest.raises(ValueError, match="too long"):
            engine.solve_linear_equation(long_eq, mode="numerical")


# ── Edge Case 2: Division by zero ────────────────────────────────────────

class TestDivisionByZero:
    def test_division_by_zero_no_crash(self):
        with pytest.raises(ValueError, match="[Dd]ivision by zero|[Cc]ould not parse"):
            engine.solve_linear_equation("x/0 = 5")

    def test_division_by_zero_numerical_no_crash(self):
        with pytest.raises(ValueError, match="[Dd]ivision by zero|[Cc]ould not parse"):
            engine.solve_linear_equation("x/0 = 5", mode="numerical")


# ── Edge Case 3: Constant equation (no variables) ───────────────────────

class TestConstantEquation:
    def test_tautology_five_equals_five(self):
        result = engine.solve_linear_equation("5 = 5")
        assert "warnings" in result
        assert any("constant" in w.lower() or "no variable" in w.lower()
                    for w in result["warnings"])
        assert "tautology" in result["final_answer"].lower() or \
               "always true" in result["final_answer"].lower()

    def test_contradiction_three_equals_seven(self):
        result = engine.solve_linear_equation("3 = 7")
        assert "warnings" in result
        assert "contradiction" in result["final_answer"].lower() or \
               "never true" in result["final_answer"].lower()
        assert result["summary"]["validation_status"] == "fail"

    def test_tautology_numerical_mode(self):
        result = engine.solve_linear_equation("5 = 5", mode="numerical")
        assert "warnings" in result
        assert "tautology" in result["final_answer"].lower() or \
               "always true" in result["final_answer"].lower()


# ── Edge Case 4: Identity equation ──────────────────────────────────────

class TestIdentityEquation:
    def test_x_equals_x_identity(self):
        result = engine.solve_linear_equation("x = x")
        assert "infinite" in result["final_answer"].lower() or \
               "identity" in result["final_answer"].lower()
        assert "warnings" in result
        assert any("identity" in w.lower() for w in result["warnings"])

    def test_two_x_plus_three_equals_two_x_plus_three(self):
        result = engine.solve_linear_equation("2x + 3 = 2x + 3")
        assert "infinite" in result["final_answer"].lower() or \
               "identity" in result["final_answer"].lower()
        assert "warnings" in result


# ── Edge Case 5: Contradiction equation ─────────────────────────────────

class TestContradictionEquation:
    def test_x_plus_three_equals_x_plus_five(self):
        result = engine.solve_linear_equation("x + 3 = x + 5")
        assert "no solution" in result["final_answer"].lower() or \
               "contradiction" in result["final_answer"].lower()
        assert "warnings" in result
        assert any("contradiction" in w.lower() for w in result["warnings"])


# ── Edge Case 6: Large coefficients in numerical mode ───────────────────

class TestLargeCoefficients:
    def test_large_coeff_warns_about_precision(self):
        result = engine.solve_linear_equation(
            "99999999999999999x = 1", mode="numerical"
        )
        assert "warnings" in result
        assert any("precision" in w.lower() for w in result["warnings"])
        # Should still produce a result (not crash)
        assert "x =" in result["final_answer"]

    def test_large_coeff_symbolic_no_warning(self):
        """Symbolic mode handles large coefficients exactly — no warning needed."""
        result = engine.solve_linear_equation("99999999999999999x = 1")
        assert "warnings" not in result or not result.get("warnings")


# ── Edge Case 7: Deeply nested parentheses ──────────────────────────────

class TestDeepNesting:
    def test_deeply_nested_parens(self):
        result = engine.solve_linear_equation("((((x + 1)))) = 5")
        assert "x =" in result["final_answer"]
        assert result["summary"]["validation_status"] == "pass"

    def test_nested_with_operations(self):
        result = engine.solve_linear_equation("(((2*(x + 3)))) = 10")
        assert "x =" in result["final_answer"]
        assert result["summary"]["validation_status"] == "pass"
