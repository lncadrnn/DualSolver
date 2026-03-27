"""
DualSolver — Glassmorphism colour / theme definitions (dark-only)

Frosted-glass-inspired palette with semi-transparent-looking layers,
soft glowing borders, and a cyan accent (`#0096C7`).

Design reference:
    • Primary accent:  #0096C7 (ocean cyan)
    • Style:           Glassmorphism — layered translucent panels with
                       subtle borders, prominent rounded corners, and
                       a sense of depth / hierarchy.
    • OS blur:         Achieved via ``gui.glassmorphism`` (Windows only).
"""

# ── UI shape constants (prominent rounding for glass panels) ───────────────

CORNER_RADIUS     = 18   # primary glass-panel radius (px)
CORNER_RADIUS_SM  = 14   # smaller radius for cards / inner elements
CORNER_RADIUS_BTN = 12   # radius for buttons

# ── Glass-border highlight ─────────────────────────────────────────────────
# A thin bright-ish border colour simulating light refraction at the edge
# of a glass surface.  Used by RoundedFrame's "glass" mode.

GLASS_HIGHLIGHT = "#243050"   # subtle blue-white tint

# ── Immutable palette dict ─────────────────────────────────────────────────

DARK_PALETTE = dict(
    # --- Base layers (deepest → shallowest) ---
    BG           = "#0a0e1a",     # deep midnight navy  (window bg / blur tint)
    BG_DARKER    = "#060810",     # deepest layer  (input bar, sidebar base)
    HEADER_BG    = "#0d1224",     # header glass – one step above BG

    # --- Accent ---
    ACCENT       = "#0096C7",     # primary accent (ocean cyan)
    ACCENT_HOVER = "#00B4D8",     # lighter hover / glow variant

    # --- Typography ---
    TEXT         = "#b8c0d8",     # main body text (soft blue-white)
    TEXT_DIM     = "#8090b0",     # secondary / dimmed labels
    TEXT_BRIGHT  = "#e8ecf4",     # headings & high-emphasis text

    # --- Glass panels ---
    USER_BG      = "#111830",     # user message bubble glass
    BOT_BG       = "#0d1228",     # bot message bubble glass
    STEP_BG      = "#101628",     # card / step glass
    STEP_BORDER  = "#1e2848",     # glass-edge border (subtle blue tint)

    # --- Semantic ---
    SUCCESS      = "#00E676",     # bright green
    ERROR        = "#FF5252",     # vivid red
    INPUT_BG     = "#0e1324",     # input field glass
    INPUT_BORDER = "#1a2545",     # input border (calm)
    VERIFY_BG    = "#081a14",     # verification background

    # --- Scrollbar ---
    SCROLLBAR_BG = "#1e2848",     # track
    SCROLLBAR_ACT= "#0096C7",    # active thumb (accent)
    SCROLLBAR_ARR= "#354065",    # arrow colour
)

# ── Case-badge colour tables (graph analysis card) ────────────────────────

DARK_CASE_COLORS = {
    "one_solution":              {"bg": "#081a14", "border": "#00E676", "fg": "#00E676"},
    "infinite":                  {"bg": "#1a1508", "border": "#FFD54F", "fg": "#FFD54F"},
    "no_solution":               {"bg": "#1a0810", "border": "#FF5252", "fg": "#FF5252"},
    "degenerate_identity":       {"bg": "#1a1508", "border": "#FFD54F", "fg": "#FFD54F"},
    "degenerate_contradiction":  {"bg": "#1a0810", "border": "#FF5252", "fg": "#FF5252"},
}

# ── Backward-compat aliases — code that still references these names ──────
LIGHT_PALETTE     = DARK_PALETTE
LIGHT_CASE_COLORS = DARK_CASE_COLORS

# ── Mutable "active" colour shortcuts ─────────────────────────────────────

BG           = DARK_PALETTE["BG"]
BG_DARKER    = DARK_PALETTE["BG_DARKER"]
HEADER_BG    = DARK_PALETTE["HEADER_BG"]
ACCENT       = DARK_PALETTE["ACCENT"]
ACCENT_HOVER = DARK_PALETTE["ACCENT_HOVER"]
TEXT         = DARK_PALETTE["TEXT"]
TEXT_DIM     = DARK_PALETTE["TEXT_DIM"]
TEXT_BRIGHT  = DARK_PALETTE["TEXT_BRIGHT"]
USER_BG      = DARK_PALETTE["USER_BG"]
BOT_BG       = DARK_PALETTE["BOT_BG"]
STEP_BG      = DARK_PALETTE["STEP_BG"]
STEP_BORDER  = DARK_PALETTE["STEP_BORDER"]
SUCCESS      = DARK_PALETTE["SUCCESS"]
ERROR        = DARK_PALETTE["ERROR"]
INPUT_BG     = DARK_PALETTE["INPUT_BG"]
INPUT_BORDER = DARK_PALETTE["INPUT_BORDER"]
VERIFY_BG    = DARK_PALETTE["VERIFY_BG"]


def palette(theme: str = "dark") -> dict:
    """Return the palette dict.  Always returns ``DARK_PALETTE``."""
    return DARK_PALETTE


def glass_highlight(theme: str = "dark") -> str:
    """Return the glass-edge highlight colour."""
    return GLASS_HIGHLIGHT


def apply_theme(theme: str = "dark") -> None:
    """No-op kept for backward compatibility — palette never changes."""
    pass
