# HydroAI Launcher PowerShell Script

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           HydroAI - Application Launcher               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Trouve le bon Python (conda environment)
$pyExe = "C:\Users\Dalton KAN'Z\.conda\envs\hydroai\python.exe"
$scriptDir = "C:\Users\Dalton KAN'Z\hydroai"

# Vérifie si Python existe
if (-not (Test-Path $pyExe)) {
    Write-Host "✗ Python not found at: $pyExe" -ForegroundColor Red
    Write-Host "`nPlease adjust the path or install conda environment" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/3] Checking Python..." -ForegroundColor Yellow
$version = & $pyExe --version 2>&1
Write-Host "  ✓ $version" -ForegroundColor Green

# Vérifie les packages
Write-Host "`n[2/3] Checking packages..." -ForegroundColor Yellow
$packages = & $pyExe -m pip list 2>$null | Select-String "numpy|scipy|PySide6"

if ($packages.Count -lt 3) {
    Write-Host "  ⚠ Some packages missing. Installing..." -ForegroundColor Yellow
    & $pyExe -m pip install numpy scipy pandas matplotlib PySide6 -q
    Write-Host "  ✓ Packages installed" -ForegroundColor Green
} else {
    Write-Host "  ✓ All packages present" -ForegroundColor Green
}

# Lance l'application
Write-Host "`n[3/3] Launching HydroAI..." -ForegroundColor Yellow
Write-Host "  ⏳ Wait for window to appear..." -ForegroundColor Gray

& $pyExe "$scriptDir\run_simple.py"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Application closed normally" -ForegroundColor Green
} else {
    Write-Host "`n✗ Application error (code: $LASTEXITCODE)" -ForegroundColor Red
}

Write-Host "`n╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
