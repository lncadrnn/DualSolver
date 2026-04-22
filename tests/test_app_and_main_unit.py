from gui.app import DualSolverApp
import gui.app as app_module
import main as entry


class _FakeLoading:
    def __init__(self):
        self.destroyed = False

    def destroy(self):
        self.destroyed = True


class _FakeEntry:
    def __init__(self):
        self.focused = False

    def focus_set(self):
        self.focused = True


class _FakeContainer:
    pass


class _FakeWidget:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.packed = False
        self._bg = "#000000"

    def pack(self, *args, **kwargs):
        self.packed = True

    def cget(self, key):
        return self._bg

    def configure(self, **kwargs):
        pass

    config = configure


class _FakeTk:
    X = "x"
    LEFT = "left"

    Frame = _FakeWidget
    Label = _FakeWidget


def test_friendly_error_for_parse_and_generic() -> None:
    msg_parse = DualSolverApp._friendly_error("2x +", ValueError("Could not parse expression"))
    assert "could not be parsed as valid math syntax" in msg_parse.lower()
    assert "How to fix it" in msg_parse

    msg_missing_equal = DualSolverApp._friendly_error(
        "2x + 3",
        ValueError("Equation must contain '='. Example: 3x + 2 = 7"),
    )
    assert "expression, not an equation" in msg_missing_equal.lower()
    assert "Add exactly one '=' sign" in msg_missing_equal

    msg_generic = DualSolverApp._friendly_error("2x+1=0", RuntimeError("boom"))
    assert "unexpected problem" in msg_generic.lower()
    assert "Technical detail: boom" in msg_generic


def test_show_error_ui_path_does_not_crash(monkeypatch) -> None:
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()

    class _FakeApp:
        def __init__(self):
            self._chat_frame = tk.Frame(root)
            self._bold = ("Segoe UI", 14, "bold")
            self._default = ("Segoe UI", 14)
            self._entry = _FakeEntry()
            self._PHASE_PAUSE = 0
            self._TYPING_SPEED = 0
            self.input_state = None
            self._theme = "dark"

        def _set_input_state(self, enabled: bool) -> None:
            self.input_state = enabled

        def _scroll_to_bottom(self) -> None:
            self.scrolled = True

    fake_app = _FakeApp()
    loading = _FakeLoading()

    DualSolverApp._show_error(fake_app, "Invalid equation", loading)

    assert loading.destroyed is True
    assert fake_app.input_state is True
    assert fake_app._entry.focused is True
    root.destroy()


def test_main_entry_runs_app(monkeypatch) -> None:
    called = {"mainloop": False}

    class DummyApp:
        def mainloop(self):
            called["mainloop"] = True

    monkeypatch.setattr(entry, "DualSolverApp", DummyApp)
    entry.main()
    assert called["mainloop"] is True
