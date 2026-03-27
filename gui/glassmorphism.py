"""
DualSolver — Glassmorphism window blur effect (Windows only).

Applies a real frosted-glass (acrylic / blur-behind) effect to a tkinter
window on Windows 10/11.  Falls back gracefully on macOS / Linux or when
the required libraries are unavailable.

Strategy
--------
1. **pywinstyles** — cleanest API; ``pywinstyles.apply_style(win, "acrylic")``
   enables Windows' built-in acrylic blur.
2. **ctypes fallback** — calls ``SetWindowCompositionAttribute`` via ctypes
   to enable blur-behind on the window handle (HWND).
3. **No-op** — if neither method succeeds the window simply keeps its
   normal background colour.  The glassmorphism palette still looks great
   even without the blur.

Usage
-----
    from gui.glassmorphism import apply_blur

    class App(tk.Tk):
        def __init__(self):
            super().__init__()
            apply_blur(self)
"""

from __future__ import annotations

import sys
import ctypes
import ctypes.wintypes
import struct


def apply_blur(window, *, style: str = "acrylic") -> bool:
    """Apply a frosted-glass blur effect to a tkinter ``Tk`` or ``Toplevel``.

    Parameters
    ----------
    window : tk.Tk | tk.Toplevel
        The target window.  Must already be fully initialised (geometry set).
    style : str
        Desired effect — ``"acrylic"`` (default) or ``"mica"`` (Win 11 only).

    Returns
    -------
    bool
        ``True`` if the blur was applied successfully.

    Notes
    -----
    • **Windows-only.**  Returns ``False`` immediately on other platforms.
    • Requires Windows 10 build 17134+ for acrylic, Windows 11 for mica.
    • The window background colour acts as a *tint* through the acrylic
      layer — a very dark navy (``#0a0e1a``) creates the classic
      glassmorphism look.
    """
    if sys.platform != "win32":
        return False

    # Ensure the window is mapped so we can get a valid HWND
    window.update_idletasks()

    # ── Attempt 1: pywinstyles ─────────────────────────────────────────
    if _try_pywinstyles(window, style):
        return True

    # ── Attempt 2: ctypes DWM blur-behind ──────────────────────────────
    if _try_ctypes_acrylic(window):
        return True

    return False


# ── pywinstyles backend ────────────────────────────────────────────────────

def _try_pywinstyles(window, style: str) -> bool:
    """Try applying blur via the ``pywinstyles`` library."""
    try:
        import pywinstyles  # type: ignore[import-untyped]
        pywinstyles.apply_style(window, style)
        return True
    except ImportError:
        return False
    except Exception:
        # Some older pywinstyles builds raise on unsupported Windows versions
        return False


# ── ctypes backend (SetWindowCompositionAttribute) ─────────────────────────

# Windows internal constants for acrylic / blur behind
_ACCENT_ENABLE_BLURBEHIND   = 3
_ACCENT_ENABLE_ACRYLICBLUR  = 4
_WCA_ACCENT_POLICY          = 19

class _ACCENT_POLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState",   ctypes.c_int),
        ("AccentFlags",   ctypes.c_int),
        ("GradientColor", ctypes.c_uint),
        ("AnimationId",   ctypes.c_int),
    ]

class _WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute",  ctypes.c_int),
        ("Data",       ctypes.POINTER(_ACCENT_POLICY)),
        ("SizeOfData", ctypes.c_size_t),
    ]


def _try_ctypes_acrylic(window) -> bool:
    """Apply acrylic blur via ``SetWindowCompositionAttribute`` (Win10+)."""
    try:
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        if not hwnd:
            return False

        # Tint colour in ABGR format — 80 alpha, dark navy tint
        #   A=0x80, B=0x1a, G=0x0e, R=0x0a  →  0x801a0e0a
        tint_abgr = 0x801a0e0a

        accent = _ACCENT_POLICY()
        accent.AccentState = _ACCENT_ENABLE_ACRYLICBLUR
        accent.GradientColor = tint_abgr

        data = _WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = _WCA_ACCENT_POLICY
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = ctypes.sizeof(accent)

        _SetWindowCompositionAttribute = ctypes.windll.user32.SetWindowCompositionAttribute
        _SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
        return True
    except Exception:
        return False
