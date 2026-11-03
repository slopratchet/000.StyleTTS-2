@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

title Audio Mastering Chain - Vocoder De-Bleed and Normalization

set "PATH=%~dp0python_embeded;%~dp0python_embeded\Scripts;%PATH%"

echo ========================================================
echo     Audio Mastering Chain: Vocoder De-Bleed and EBU R128
echo ========================================================
echo Target Specs: -23.0 LUFS ^| -1.0 dBFS True Peak ^| Zero-Phase Rolloff
echo ========================================================
echo.

set "PROCESSED_COUNT=0"

if "%~1"=="" goto default_mode

:arg_loop
if "%~1"=="" goto check_summary
if exist "%~1" (
    echo [*] Mastering: "%~f1"
    python_embeded\python.exe scripts\master_audio.py --input "%~f1"
    set /a PROCESSED_COUNT+=1
    echo.
) else (
    echo [WARNING] Audio file not found: "%~1"
    echo.
)
shift
goto arg_loop

:default_mode
if exist "%~dp0output\test_blend.wav" (
    echo [*] Mastering default blend: "%~dp0output\test_blend.wav"
    python_embeded\python.exe scripts\master_audio.py --input "%~dp0output\test_blend.wav"
    set /a PROCESSED_COUNT+=1
    echo.
)

if exist "%~dp0output\test_blend_adjusted.wav" (
    echo [*] Mastering adjusted blend: "%~dp0output\test_blend_adjusted.wav"
    python_embeded\python.exe scripts\master_audio.py --input "%~dp0output\test_blend_adjusted.wav"
    set /a PROCESSED_COUNT+=1
    echo.
)

:check_summary
if !PROCESSED_COUNT! EQU 0 (
    echo [ERROR] No audio files found to master.
    echo Expected at least one of:
    echo   - "%~dp0output\test_blend.wav"
    echo   - "%~dp0output\test_blend_adjusted.wav"
    echo.
    echo Please run merge_voices.bat or adjust_voice.bat first,
    echo or drag-and-drop one or more .wav files onto this batch file.
    echo.
    pause
    exit /b 1
)

echo ========================================================
echo Mastering completed successfully: !PROCESSED_COUNT! file(s) processed.
echo ========================================================
pause
