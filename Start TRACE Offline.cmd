@echo off
setlocal
cd /d "%~dp0"
if exist "%~dp0.runtime\Scripts\python.exe" (
    "%~dp0.runtime\Scripts\python.exe" "%~dp0scripts\run_offline.py" %*
) else if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0scripts\run_offline.py" %*
) else (
    py -3 "%~dp0scripts\run_offline.py" %*
)
if errorlevel 1 pause
