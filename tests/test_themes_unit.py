from gui import themes


def test_palette_returns_expected_dict() -> None:
    assert themes.palette("dark") == themes.DARK_PALETTE
    assert themes.palette("light") == themes.LIGHT_PALETTE


def test_apply_theme_updates_module_globals() -> None:
    themes.apply_theme("light")
    assert themes.BG == themes.LIGHT_PALETTE["BG"]
    assert themes.ERROR == themes.LIGHT_PALETTE["ERROR"]

    themes.apply_theme("dark")
    assert themes.BG == themes.DARK_PALETTE["BG"]
    assert themes.ERROR == themes.DARK_PALETTE["ERROR"]


def test_theme_aliases_and_palette_metadata() -> None:
    assert themes.normalize_theme("dark") == "ocean"
    assert themes.normalize_theme("green") == "emerald"
    assert themes.normalize_theme("unknown-theme") == "ocean"

    choices = themes.available_themes()
    assert len(choices) >= 5
    assert all("id" in item and "label" in item and "accent" in item for item in choices)
