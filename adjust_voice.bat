@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

title Voice Pitch and Rate Adjuster

set "PATH=%~dp0python_embeded;%~dp0python_embeded\Scripts;%PATH%"

echo ========================================================
echo             Voice Pitch and Rate Adjuster               
echo ========================================================
echo.

set "TARGET_FILE=%~1"
if "%TARGET_FILE%"=="" (
    set "TARGET_FILE=%~dp0output\test_blend.wav"
)

if not exist "!TARGET_FILE!" (
    echo [ERROR] Target audio file not found at:
    echo "!TARGET_FILE!"
    echo.
    echo Please make sure output\test_blend.wav exists,
    echo or drag-and-drop any .wav file onto this batch file.
    echo.
    pause
    exit /b 1
)

echo Target Audio: "!TARGET_FILE!"
echo.
echo --------------------------------------------------------
echo 1. Pitch Adjustment (Semitones)
echo    Examples:
echo      +2.0  = 2 semitones higher (higher pitch)
echo      -1.5  = 1.5 semitones lower (deeper voice)
echo       0.0  = No pitch change (original pitch)
echo --------------------------------------------------------
set "PITCH=0.0"
set "USER_PITCH="
set /p "USER_PITCH=Enter pitch shift in semitones [default 0.0]: "
if defined USER_PITCH (
    for /f "tokens=* delims= " %%A in ("!USER_PITCH!") do set "USER_PITCH=%%A"
    if not "!USER_PITCH!"=="" set "PITCH=!USER_PITCH!"
)

echo.
echo --------------------------------------------------------
echo 2. Rate / Speed Multiplier
echo    Examples:
echo       1.15 = 15%% faster playback
echo       0.90 = 10%% slower / deliberate pacing
echo       1.00 = Original playback speed
echo --------------------------------------------------------
set "RATE=1.0"
set "USER_RATE="
set /p "USER_RATE=Enter rate multiplier [default 1.0]: "
if defined USER_RATE (
    for /f "tokens=* delims= " %%A in ("!USER_RATE!") do set "USER_RATE=%%A"
    if not "!USER_RATE!"=="" set "RATE=!USER_RATE!"
)

echo.
echo [*] Processing audio with Pitch: !PITCH! semitones and Rate: !RATE!x...
echo.

python_embeded\python.exe scripts\adjust_voice.py --input "!TARGET_FILE!" --pitch "!PITCH!" --rate "!RATE!"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Pitch and rate adjustment failed. See error messages above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo Adjustment complete!
echo ========================================================
pause
