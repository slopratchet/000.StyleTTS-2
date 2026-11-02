@echo off
setlocal
cd /d "%~dp0"

set "PATH=%~dp0python_embeded;%~dp0python_embeded\Scripts;%PATH%"

echo ========================================================
echo    Automating Audio Pre-Processing (DSP Hygiene)
echo ========================================================

python_embeded\python.exe scripts\preprocess_audio.py %*

echo.
pause

