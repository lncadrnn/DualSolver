# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for DualSolver — folder distribution (one-dir mode).
# Run via: build.bat  (or: .venv\Scripts\pyinstaller.exe DualSolver.spec)

from PyInstaller.utils.hooks import collect_all, collect_data_files

# Collect all of sympy — it uses heavy internal dynamic imports that the
# standard analysis pass misses, so collect_all is the safest approach.
sympy_datas, sympy_binaries, sympy_hiddenimports = collect_all('sympy')

# Collect matplotlib data files (fonts, style sheets, etc.)
mpl_datas = collect_data_files('matplotlib')

import os as _os

# Several DLLs that Python extension modules depend on live in the conda
# Library/bin folder and are not on PATH, so PyInstaller can't resolve them
# automatically.  Enumerate them all explicitly.
_conda_bin = _os.path.join(SPECPATH, '.conda', 'Library', 'bin')
_extra_dlls = (
    'tcl86t.dll',       # Tcl/Tk — needed by _tkinter.pyd
    'tk86t.dll',        # Tcl/Tk — needed by _tkinter.pyd
    'ffi.dll',          # libffi  — needed by _ctypes.pyd
    'libmpdec-4.dll',   # mpdec   — needed by _decimal.pyd
    'liblzma.dll',      # lzma    — needed by _lzma.pyd
    'libbz2.dll',       # bz2     — needed by _bz2.pyd
    'libexpat.dll',     # expat   — needed by pyexpat.pyd
    'zstd.dll',         # zstd    — needed by _zstd.pyd
)
_tk_binaries = []
for _dll in _extra_dlls:
    _src = _os.path.join(_conda_bin, _dll)
    if _os.path.exists(_src):
        _tk_binaries.append((_src, '.'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[*sympy_binaries, *_tk_binaries],
    datas=[
        ('assets', 'assets'),   # logo.png, back.png, icon.ico → _internal/assets/
        *sympy_datas,
        *mpl_datas,
    ],
    hiddenimports=[
        # Matplotlib Tkinter backend — not auto-detected
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends._backend_tk',
        # Pillow Tkinter bridge
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        # SymPy collected above
        *sympy_hiddenimports,
        # fpdf2
        'fpdf',
        # tkinter extras
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # GUI toolkits we don't use
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'wx',
        # Dev / test tools
        'pytest', 'IPython', 'jupyter', 'notebook', 'sphinx',
        # Heavy scientific packages not in requirements
        'scipy', 'pandas', 'sklearn',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,      # one-dir mode: binaries go to COLLECT
    name='DualSolver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,              # no terminal window — pure GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.png',     # Pillow converts PNG → ICO automatically
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='DualSolver',          # output: dist/DualSolver/
)
