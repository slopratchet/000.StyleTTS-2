@echo off
setlocal
cd /d "%~dp0"

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
echo Running StyleTTS-2 Voice Merger
echo ========================================================

python_embeded\python.exe scripts\merge_voices.py

echo.
echo Process complete. Check output\ for your .pt and .wav files.
pause
