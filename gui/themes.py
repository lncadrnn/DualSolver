"""
DualSolver — Theme and colour definitions

Provides coordinated dark palettes that share the same layout language
while changing the accent family (blue, black, green, orange, red, etc.).

Design reference:
    - Style: Solid dark UI with rounded cards and clear hierarchy.
"""

import os

# ── UI shape constants ──────────────────────────────────────────────────────

CORNER_RADIUS     = 18   # primary glass-panel radius (px)
CORNER_RADIUS_SM  = 14   # smaller radius for cards / inner elements
CORNER_RADIUS_BTN = 12   # radius for buttons

# ── Legacy highlight alias ──────────────────────────────────────────────────
# Kept for compatibility with callers that still use glass_highlight().

GLASS_HIGHLIGHT = "#243050"   # subtle blue-white tint

LOGO_FILENAME = "logo.png"
_LOGO_CANDIDATES = (
    "logo.png",
    "darkmode-logo.png",
    "lightmode-logo.png",
    "noname-logo.png",
)


def logo_path() -> str:
    """Return the preferred logo path from the assets folder."""
    base = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
    )
    for fname in _LOGO_CANDIDATES:
        path = os.path.join(base, fname)
        if os.path.exists(path):
            return path
    return os.path.join(base, LOGO_FILENAME)

# ── Immutable palette dicts ────────────────────────────────────────────────

OCEAN_PALETTE = dict(
    # --- Base layers (deepest -> shallowest) ---
    BG           = "#0a0e1a",     # deep midnight navy
    BG_DARKER    = "#060810",     # deepest layer  (input bar, sidebar base)
    HEADER_BG    = "#0d1224",     # header layer one step above BG

    # --- Accent ---
    ACCENT       = "#0096C7",     # primary accent (ocean cyan)
    ACCENT_HOVER = "#00B4D8",     # lighter hover / glow variant
    ACCENT_TEXT  = "#ffffff",     # text/icon color placed on ACCENT

    # --- Typography ---
    TEXT         = "#b8c0d8",     # main body text (soft blue-white)
    TEXT_DIM     = "#8090b0",     # secondary / dimmed labels
    TEXT_BRIGHT  = "#e8ecf4",     # headings & high-emphasis text

    # --- Panel surfaces ---
    USER_BG      = "#111830",     # user message bubble
    BOT_BG       = "#0d1228",     # bot message bubble
    STEP_BG      = "#101628",     # card / step panel
    STEP_BORDER  = "#1e2848",     # panel border (subtle blue tint)

    # --- Semantic ---
    SUCCESS      = "#00E676",     # bright green
    ERROR        = "#FF5252",     # vivid red
    INPUT_BG     = "#0e1324",     # input field
    INPUT_BORDER = "#1a2545",     # input border (calm)
    VERIFY_BG    = "#081a14",     # verification background

    # --- Scrollbar ---
    SCROLLBAR_BG = "#1e2848",     # track
    SCROLLBAR_ACT= "#0096C7",     # active thumb (accent)
    SCROLLBAR_ARR= "#354065",    # arrow colour
)

OBSIDIAN_PALETTE = dict(
    BG           = "#050505",
    BG_DARKER    = "#000000",
    HEADER_BG    = "#0c0c0c",
    ACCENT       = "#f2f2f2",
    ACCENT_HOVER = "#ffffff",
    ACCENT_TEXT  = "#111111",
    TEXT         = "#c9c9c9",
    TEXT_DIM     = "#8e8e8e",
    TEXT_BRIGHT  = "#f7f7f7",
    USER_BG      = "#121212",
    BOT_BG       = "#0d0d0d",
    STEP_BG      = "#151515",
    STEP_BORDER  = "#2b2b2b",
    SUCCESS      = "#39d98a",
    ERROR        = "#ff5e5e",
    INPUT_BG     = "#111111",
    INPUT_BORDER = "#2a2a2a",
    VERIFY_BG    = "#0b1510",
    SCROLLBAR_BG = "#2b2b2b",
    SCROLLBAR_ACT= "#f2f2f2",
    SCROLLBAR_ARR= "#666666",
)

EMERALD_PALETTE = dict(
    BG           = "#08120d",
    BG_DARKER    = "#040a07",
    HEADER_BG    = "#0b1711",
    ACCENT       = "#22c55e",
    ACCENT_HOVER = "#4ade80",
    ACCENT_TEXT  = "#05210f",
    TEXT         = "#b9d8c8",
    TEXT_DIM     = "#7ba08e",
    TEXT_BRIGHT  = "#e6f4ec",
    USER_BG      = "#0f1d16",
    BOT_BG       = "#0b1711",
    STEP_BG      = "#0f1a14",
    STEP_BORDER  = "#1c3a2a",
    SUCCESS      = "#4ade80",
    ERROR        = "#ff6b6b",
    INPUT_BG     = "#0d1712",
    INPUT_BORDER = "#1b3a2b",
    VERIFY_BG    = "#082015",
    SCROLLBAR_BG = "#1b3a2b",
    SCROLLBAR_ACT= "#22c55e",
    SCROLLBAR_ARR= "#4a6b5a",
)

SUNSET_PALETTE = dict(
    BG           = "#151009",
    BG_DARKER    = "#0f0904",
    HEADER_BG    = "#1a1209",
    ACCENT       = "#f97316",
    ACCENT_HOVER = "#fb923c",
    ACCENT_TEXT  = "#2b1300",
    TEXT         = "#e0c8b4",
    TEXT_DIM     = "#aa8b73",
    TEXT_BRIGHT  = "#faeee5",
    USER_BG      = "#24170d",
    BOT_BG       = "#1d130b",
    STEP_BG      = "#24170d",
    STEP_BORDER  = "#4a2d17",
    SUCCESS      = "#4ade80",
    ERROR        = "#ff6b6b",
    INPUT_BG     = "#1a1209",
    INPUT_BORDER = "#4a2d17",
    VERIFY_BG    = "#1b1d0b",
    SCROLLBAR_BG = "#4a2d17",
    SCROLLBAR_ACT= "#f97316",
    SCROLLBAR_ARR= "#8c6040",
)

CRIMSON_PALETTE = dict(
    BG           = "#15090d",
    BG_DARKER    = "#0f0508",
    HEADER_BG    = "#1a0a10",
    ACCENT       = "#ef4444",
    ACCENT_HOVER = "#f87171",
    ACCENT_TEXT  = "#ffffff",
    TEXT         = "#dec0ca",
    TEXT_DIM     = "#ab7f8d",
    TEXT_BRIGHT  = "#f8e9ee",
    USER_BG      = "#241018",
    BOT_BG       = "#1d0d13",
    STEP_BG      = "#241018",
    STEP_BORDER  = "#4b1d2d",
    SUCCESS      = "#34d399",
    ERROR        = "#ff5c75",
    INPUT_BG     = "#1a0b11",
    INPUT_BORDER = "#4b1d2d",
    VERIFY_BG    = "#1b0e12",
    SCROLLBAR_BG = "#4b1d2d",
    SCROLLBAR_ACT= "#ef4444",
    SCROLLBAR_ARR= "#8e4f63",
)

VIOLET_PALETTE = dict(
    BG           = "#100c1a",
    BG_DARKER    = "#0a0712",
    HEADER_BG    = "#150f24",
    ACCENT       = "#8b5cf6",
    ACCENT_HOVER = "#a78bfa",
    ACCENT_TEXT  = "#ffffff",
    TEXT         = "#d0c4e9",
    TEXT_DIM     = "#9481b8",
    TEXT_BRIGHT  = "#efe9fb",
    USER_BG      = "#1a1430",
    BOT_BG       = "#161128",
    STEP_BG      = "#1a1430",
    STEP_BORDER  = "#33265a",
    SUCCESS      = "#34d399",
    ERROR        = "#ff6b81",
    INPUT_BG     = "#151028",
    INPUT_BORDER = "#33265a",
    VERIFY_BG    = "#121326",
    SCROLLBAR_BG = "#33265a",
    SCROLLBAR_ACT= "#8b5cf6",
    SCROLLBAR_ARR= "#6e5d92",
)


THEME_PALETTES = {
    "ocean": OCEAN_PALETTE,
    "obsidian": OBSIDIAN_PALETTE,
    "emerald": EMERALD_PALETTE,
    "sunset": SUNSET_PALETTE,
    "crimson": CRIMSON_PALETTE,
    "violet": VIOLET_PALETTE,
}

THEME_ORDER = ["ocean", "obsidian", "emerald", "sunset", "crimson", "violet"]

THEME_LABELS = {
    "ocean": "Ocean Blue",
    "obsidian": "Obsidian Black",
    "emerald": "Emerald Green",
    "sunset": "Sunset Orange",
    "crimson": "Crimson Red",
    "violet": "Violet",
}

THEME_ALIASES = {
    "dark": "ocean",
    "light": "ocean",
    "blue": "ocean",
    "black": "obsidian",
    "green": "emerald",
    "orange": "sunset",
    "red": "crimson",
}

# ── Case-badge colour tables (graph analysis card) ────────────────────────

DARK_CASE_COLORS = {
    "one_solution":              {"bg": "#081a14", "border": "#00E676", "fg": "#00E676"},
    "infinite":                  {"bg": "#1a1508", "border": "#FFD54F", "fg": "#FFD54F"},
    "no_solution":               {"bg": "#1a0810", "border": "#FF5252", "fg": "#FF5252"},
    "degenerate_identity":       {"bg": "#1a1508", "border": "#FFD54F", "fg": "#FFD54F"},
    "degenerate_contradiction":  {"bg": "#1a0810", "border": "#FF5252", "fg": "#FF5252"},
}

# ── Backward-compat aliases — code that still references these names ──────
LIGHT_PALETTE     = OCEAN_PALETTE
LIGHT_CASE_COLORS = DARK_CASE_COLORS
DARK_PALETTE      = OCEAN_PALETTE


def normalize_theme(theme: str = "dark") -> str:
    """Normalize a stored/user theme id to a supported theme key."""
    key = (theme or "dark").strip().lower()
    key = THEME_ALIASES.get(key, key)
    if key not in THEME_PALETTES:
        return "ocean"
    return key


def available_themes() -> list[dict]:
    """Return theme metadata for settings palette pickers."""
    themes_list = []
    for key in THEME_ORDER:
        p = THEME_PALETTES[key]
        themes_list.append({
            "id": key,
            "label": THEME_LABELS.get(key, key.title()),
            "accent": p["ACCENT"],
            "accent_text": p["ACCENT_TEXT"],
        })
    return themes_list


_ACTIVE_THEME = normalize_theme("dark")

# ── Mutable "active" colour shortcuts ─────────────────────────────────────

BG           = OCEAN_PALETTE["BG"]
BG_DARKER    = OCEAN_PALETTE["BG_DARKER"]
HEADER_BG    = OCEAN_PALETTE["HEADER_BG"]
ACCENT       = OCEAN_PALETTE["ACCENT"]
ACCENT_HOVER = OCEAN_PALETTE["ACCENT_HOVER"]
ACCENT_TEXT  = OCEAN_PALETTE["ACCENT_TEXT"]
TEXT         = OCEAN_PALETTE["TEXT"]
TEXT_DIM     = OCEAN_PALETTE["TEXT_DIM"]
TEXT_BRIGHT  = OCEAN_PALETTE["TEXT_BRIGHT"]
USER_BG      = OCEAN_PALETTE["USER_BG"]
BOT_BG       = OCEAN_PALETTE["BOT_BG"]
STEP_BG      = OCEAN_PALETTE["STEP_BG"]
STEP_BORDER  = OCEAN_PALETTE["STEP_BORDER"]
SUCCESS      = OCEAN_PALETTE["SUCCESS"]
ERROR        = OCEAN_PALETTE["ERROR"]
INPUT_BG     = OCEAN_PALETTE["INPUT_BG"]
INPUT_BORDER = OCEAN_PALETTE["INPUT_BORDER"]
VERIFY_BG    = OCEAN_PALETTE["VERIFY_BG"]


def palette(theme: str = "dark") -> dict:
    """Return the palette dict for *theme* (accepts legacy aliases)."""
    return THEME_PALETTES[normalize_theme(theme)]


def glass_highlight(theme: str = "dark") -> str:
    """Return legacy highlight colour kept for compatibility."""
    return GLASS_HIGHLIGHT


def apply_theme(theme: str = "dark") -> None:
    """Apply *theme* to module-level mutable colour shortcuts."""
    global _ACTIVE_THEME
    global BG, BG_DARKER, HEADER_BG
    global ACCENT, ACCENT_HOVER, ACCENT_TEXT
    global TEXT, TEXT_DIM, TEXT_BRIGHT
    global USER_BG, BOT_BG, STEP_BG, STEP_BORDER
    global SUCCESS, ERROR, INPUT_BG, INPUT_BORDER, VERIFY_BG

    _ACTIVE_THEME = normalize_theme(theme)
    p = THEME_PALETTES[_ACTIVE_THEME]

    BG = p["BG"]
    BG_DARKER = p["BG_DARKER"]
    HEADER_BG = p["HEADER_BG"]
    ACCENT = p["ACCENT"]
    ACCENT_HOVER = p["ACCENT_HOVER"]
    ACCENT_TEXT = p["ACCENT_TEXT"]
    TEXT = p["TEXT"]
    TEXT_DIM = p["TEXT_DIM"]
    TEXT_BRIGHT = p["TEXT_BRIGHT"]
    USER_BG = p["USER_BG"]
    BOT_BG = p["BOT_BG"]
    STEP_BG = p["STEP_BG"]
    STEP_BORDER = p["STEP_BORDER"]
    SUCCESS = p["SUCCESS"]
    ERROR = p["ERROR"]
    INPUT_BG = p["INPUT_BG"]
    INPUT_BORDER = p["INPUT_BORDER"]
    VERIFY_BG = p["VERIFY_BG"]
