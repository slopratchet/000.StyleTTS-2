@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

title StyleTTS-2 - Dialogue Synthesizer

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
echo        StyleTTS-2 Merged Voice Dialogue Synthesizer     
echo ========================================================

if not exist "%~dp0output\merged_identity.pt" (
    echo [ERROR] No merged voice identity found at output\merged_identity.pt
    echo.
    echo Please run 'merge_voices.bat' first to blend your voices.
    echo.
    pause
    exit /b 1
)

set "INPUT_ARG=%~1"

:: If a file path was passed or dragged onto the bat
if not "%INPUT_ARG%"=="" (
    if exist "%INPUT_ARG%" (
        echo [*] Using dialogue text from file: "%INPUT_ARG%"
        python_embeded\python.exe scripts\synthesize_dialogue.py --text-file "%INPUT_ARG%"
        goto DONE
    ) else (
        echo [*] Synthesizing supplied text argument...
        python_embeded\python.exe scripts\synthesize_dialogue.py --text "%INPUT_ARG%"
        goto DONE
    )
)

:: Check if input\dialogue.txt exists with text
if exist "%~dp0input\dialogue.txt" (
    echo [INFO] Found '%~dp0input\dialogue.txt'.
    set /p "USE_FILE=Do you want to use input\dialogue.txt? [Y/N, default Y]: "
    if /i "!USE_FILE!"=="" set "USE_FILE=Y"
    if /i "!USE_FILE!"=="Y" (
        python_embeded\python.exe scripts\synthesize_dialogue.py --text-file "%~dp0input\dialogue.txt"
        goto DONE
    )
)

:: Otherwise prompt interactively
echo.
echo Enter the dialogue text you want your merged voice to speak:
set /p "USER_TEXT=> "

if "!USER_TEXT!"=="" (
    echo [ERROR] No dialogue entered.
    pause
    exit /b 1
)

python_embeded\python.exe scripts\synthesize_dialogue.py --text "!USER_TEXT!"

:DONE
echo.
echo ========================================================
echo Done! Audio exported to output\ (also as dialogue_latest.wav)
echo ========================================================
pause

