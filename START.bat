@echo off
REM Script de lancement HydroAI pour Windows

cd /d "C:\Users\Dalton KAN'Z\hydroai"

REM Verify Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python first.
    pause
    exit /b 1
)

REM Install packages if needed
echo Checking dependencies...
python -c "import numpy, scipy, pandas, PySide6, matplotlib" >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing missing packages...
    python -m pip install numpy scipy pandas PySide6 matplotlib --quiet
)

REM Launch application
echo Launching HydroAI...
python launcher.py

if %errorlevel% neq 0 (
    echo Error launching application
    pause
)
