@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

title StyleTTS-2 - Voice Merger

set "PATH=%~dp0python_embeded;%~dp0python_embeded\Scripts;%~dp0espeak-ng;C:\Program Files\eSpeak NG;%PATH%"
if exist "C:\Program Files\eSpeak NG\libespeak-ng.dll" (
    set "PHONEMIZER_ESPEAK_PATH=C:\Program Files\eSpeak NG\libespeak-ng.dll"
    set "PHONEMIZER_ESPEAK_LIBRARY=C:\Program Files\eSpeak NG\libespeak-ng.dll"
) else if exist "%~dp0espeak-ng\libespeak-ng.dll" (
    set "PHONEMIZER_ESPEAK_PATH=%~dp0espeak-ng\libespeak-ng.dll"
    set "PHONEMIZER_ESPEAK_LIBRARY=%~dp0espeak-ng\libespeak-ng.dll"
    set "ESPEAK_DATA_PATH=%~dp0espeak-ng"
)

echo ========================================================
echo             StyleTTS-2 Voice Identity Merger            
echo ========================================================

set "VOICE_A=%~1"
set "VOICE_B=%~2"

if "%VOICE_A%"=="" set "VOICE_A=%~dp0input\voice_a.wav"
if "%VOICE_B%"=="" set "VOICE_B=%~dp0input\voice_b.wav"

if not exist "%VOICE_A%" (
    echo [ERROR] Voice A file not found at:
    echo "%VOICE_A%"
    echo.
    echo Please place a reference .wav at input\voice_a.wav
    echo or drag-and-drop two .wav files onto this batch file.
    echo.
    pause
    exit /b 1
)

if not exist "%VOICE_B%" (
    echo [ERROR] Voice B file not found at:
    echo "%VOICE_B%"
    echo.
    echo Please place a reference .wav at input\voice_b.wav
    echo or drag-and-drop two .wav files onto this batch file.
    echo.
    pause
    exit /b 1
)

echo Using Voice A: "%VOICE_A%"
echo Using Voice B: "%VOICE_B%"
echo.
echo Ratio explanation:
echo   1.0 = 100%% Voice A
echo   0.0 = 100%% Voice B
echo   0.5 = 50/50 blend (recommended)
echo.

set "RATIO=0.5"
set /p "USER_RATIO=Enter blend ratio [default 0.5]: "
if not "!USER_RATIO!"=="" set "RATIO=!USER_RATIO!"

echo.
echo [*] Merging voices with ratio !RATIO!...
python_embeded\python.exe scripts\merge_voices.py --voice-a "%VOICE_A%" --voice-b "%VOICE_B%" --ratio !RATIO!

echo.
echo ========================================================
echo Done! Merged voice embedding saved to output\merged_identity.pt
echo Test sample exported to output\test_blend.wav
echo ========================================================
pause

