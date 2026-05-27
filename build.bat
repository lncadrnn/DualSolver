@echo off
title DualSolver Build
setlocal enabledelayedexpansion

echo.
echo ==========================================
echo   DualSolver ^| Building Windows App
echo ==========================================
echo.

set "VENV_PY=.venv\Scripts\python.exe"
set "VENV_PIP=.venv\Scripts\pip.exe"
set "VENV_PYIN=.venv\Scripts\pyinstaller.exe"

:: Verify the virtual environment exists
if not exist "%VENV_PY%" (
    echo ERROR: .venv not found. Create it first:
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

:: Install PyInstaller into the project venv if missing
echo [1/4] Checking PyInstaller...
%VENV_PIP% show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    %VENV_PIP% install pyinstaller --quiet
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller.
        pause
        exit /b 1
    )
) else (
    echo       PyInstaller already installed.
)

:: Remove previous build artifacts
echo [2/4] Cleaning previous build...
if exist build   rmdir /s /q build
if exist dist    rmdir /s /q dist

:: Run PyInstaller
echo [3/4] Building with PyInstaller...
"%VENV_PYIN%" DualSolver.spec --noconfirm
if errorlevel 1 (
    echo.
    echo ERROR: Build failed. See output above for details.
    pause
    exit /b 1
)

:: Remove build/ — it contains an incomplete intermediate EXE that crashes if run.
:: Only dist\DualSolver\ is the real, runnable output.
echo [4/4] Cleaning intermediate build artifacts...
if exist build rmdir /s /q build

echo.
echo ==========================================
echo   Build complete!
echo   Output: dist\DualSolver\DualSolver.exe
echo ==========================================
echo.
echo Tip: Copy the entire dist\DualSolver\ folder
echo      to share the app — do not move just the EXE.
echo.
pause
