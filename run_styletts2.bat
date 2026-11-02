@echo off
setlocal enabledelayedexpansion
title StyleTTS-2 Local Automation Pipeline

echo ===================================================
echo       StyleTTS-2 Local Automation Launcher        
echo ===================================================

:: 1. Identify Python interpreter
set "PY_CMD="

if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.venv\Scripts\python.exe"
    echo [INFO] Found existing virtual environment in .venv
    goto :PYTHON_READY
)

:: Try py launcher for Python 3.10
py -3.10 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Creating Python 3.10 virtual environment...
    py -3.10 -m venv .venv
    if exist ".venv\Scripts\python.exe" (
        set "PY_CMD=.venv\Scripts\python.exe"
        goto :PYTHON_READY
    )
)

:: Try direct Python 3.10 path if installed in standard location
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    echo [INFO] Found Python 3.10. Creating .venv...
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" -m venv .venv
    if exist ".venv\Scripts\python.exe" (
        set "PY_CMD=.venv\Scripts\python.exe"
        goto :PYTHON_READY
    )
)

:: Fallback to default python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Creating virtual environment using system Python...
    python -m venv .venv
    if exist ".venv\Scripts\python.exe" (
        set "PY_CMD=.venv\Scripts\python.exe"
        goto :PYTHON_READY
    ) else (
        set "PY_CMD=python"
        goto :PYTHON_READY
    )
)

echo [ERROR] No suitable Python installation found! Please install Python 3.10 (64-bit).
pause
exit /b 1

:PYTHON_READY
echo [INFO] Using Python: %PY_CMD%

:: Check if packages are installed
"%PY_CMD%" -c "import torch; import styletts2" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [SETUP REQUIRED] Dependencies are missing. Running setup script...
    "%PY_CMD%" scripts\setup_styletts2.py
    if %errorlevel% neq 0 (
        echo [ERROR] Dependency installation encountered issues.
        pause
    )
)

:MENU
cls
echo ===================================================
echo             StyleTTS-2 Control Panel               
echo ===================================================
echo [1] Interactive Speech Synthesis (CLI prompt)
echo [2] Process Pending Batch in 'input/' (Single Pass)
echo [3] Start Continuous Worker-Sower Watcher
echo [4] Download / Verify Pre-trained Models
echo [5] Run / Repair Setup (Install Dependencies)
echo [6] Exit
echo ===================================================
set /p choice="Select an option (1-6): "

if "%choice%"=="1" (
    echo.
    echo Starting Interactive Synthesis...
    "%PY_CMD%" scripts\inference.py --interactive
    pause
    goto MENU
)

if "%choice%"=="2" (
    echo.
    echo Processing pending batch from 'input/'...
    "%PY_CMD%" scripts\worker_sower_router.py
    pause
    goto MENU
)

if "%choice%"=="3" (
    echo.
    echo Starting continuous worker-sower watcher...
    echo (Place .txt prompt files and optional .wav reference audio in 'input/')
    echo Press Ctrl+C to stop watching.
    "%PY_CMD%" scripts\worker_sower_router.py --watch
    pause
    goto MENU
)

if "%choice%"=="4" (
    echo.
    echo Checking and downloading models...
    "%PY_CMD%" scripts\fetch_models.py
    pause
    goto MENU
)

if "%choice%"=="5" (
    echo.
    echo Running setup script...
    "%PY_CMD%" scripts\setup_styletts2.py
    pause
    goto MENU
)

if "%choice%"=="6" (
    echo Exiting StyleTTS-2. Goodbye!
    exit /b 0
)

echo Invalid choice. Please choose 1-6.
timeout /t 2 >nul
goto MENU

