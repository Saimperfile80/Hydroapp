@echo off
setlocal enabledelayedexpansion

echo Verification des packages PySide6...

cd /D "C:\Users\Dalton KAN'Z\hydroai"

REM Utiliser le Python conda
set PYTHON="C:\Users\Dalton KAN'Z\hydroai\.conda\python.exe"

REM Installer packages si manquants
echo Installation des dependances...
%PYTHON% -m pip install --quiet numpy scipy pandas matplotlib PySide6 reportlab 2>nul

REM Lancer l'app
echo Demarrage HydroAI...
%PYTHON% run_simple.py

pause
