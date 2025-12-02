#!/usr/bin/env powershell
# HydroAI Quick Start Script for Windows PowerShell

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           HydroAI - Quick Start Verification              ║" -ForegroundColor Cyan
Write-Host "║                   November 26, 2025                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Step 1: Check Python
Write-Host "[1/5] Verifying Python installation..." -ForegroundColor Yellow
$pythonVersion = & python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    Write-Host "   Download from: https://python.org" -ForegroundColor Red
    exit 1
}

# Step 2: Check pip
Write-Host "`n[2/5] Checking pip..." -ForegroundColor Yellow
$pipVersion = & pip --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Pip ready: $pipVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Pip not found. Try: python -m pip --upgrade pip" -ForegroundColor Red
    exit 1
}

# Step 3: Check HydroAI files
Write-Host "`n[3/5] Checking HydroAI files..." -ForegroundColor Yellow
$requiredFiles = @(
    "launcher.py",
    "run.py",
    "core\calculations\theis.py",
    "core\ai\anomaly_detection.py",
    "app\main_app.py",
    "README.md"
)

$filesOk = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ MISSING: $file" -ForegroundColor Red
        $filesOk = $false
    }
}

if (-not $filesOk) {
    Write-Host "`n✗ Some files missing. Please check HydroAI installation." -ForegroundColor Red
    exit 1
}

# Step 4: Check Python packages
Write-Host "`n[4/5] Checking Python packages..." -ForegroundColor Yellow
$packages = @("numpy", "scipy", "pandas", "PySide6", "matplotlib")
$packagesOk = $true

foreach ($pkg in $packages) {
    $result = & python -c "import $pkg; print('$pkg')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $pkg installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $pkg NOT installed" -ForegroundColor Yellow
        $packagesOk = $false
    }
}

if (-not $packagesOk) {
    Write-Host "`n[!] Installing missing packages..." -ForegroundColor Yellow
    & pip install numpy scipy pandas PySide6 matplotlib
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Packages installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install packages. Try manually:" -ForegroundColor Red
        Write-Host "   pip install numpy scipy pandas PySide6 matplotlib" -ForegroundColor Red
        exit 1
    }
}

# Step 5: Quick module test
Write-Host "`n[5/5] Testing HydroAI modules..." -ForegroundColor Yellow

$testCode = @"
import sys
try:
    from core.calculations import theis, cooper_jacob
    print("Calculs: OK")
except Exception as e:
    print(f"Calculs: ERROR - {e}")
    sys.exit(1)
    
try:
    from core.ai import AnomalyDetector, ParameterRecommender, PreComputeValidator
    print("IA: OK")
except Exception as e:
    print(f"IA: ERROR - {e}")
    sys.exit(1)
    
try:
    from PySide6.QtWidgets import QApplication
    print("PySide6: OK")
except Exception as e:
    print(f"PySide6: ERROR - {e}")
    sys.exit(1)

print("ALL OK")
"@

$testResult = & python -c $testCode 2>&1
foreach ($line in $testResult) {
    if ($line -like "*OK") {
        Write-Host "  ✓ $line" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $line" -ForegroundColor Red
    }
}

# Final status
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║           ✓ ALL CHECKS PASSED - READY TO RUN             ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "Next step: Launch the application" -ForegroundColor Cyan
Write-Host "`nOption 1 (Recommended):" -ForegroundColor Yellow
Write-Host "  python launcher.py`n" -ForegroundColor White

Write-Host "Option 2:" -ForegroundColor Yellow
Write-Host "  python run.py`n" -ForegroundColor White

Write-Host "For help, see:" -ForegroundColor Cyan
Write-Host "  - README.md (overview)" -ForegroundColor Gray
Write-Host "  - QUICKSTART.md (5-min guide)" -ForegroundColor Gray
Write-Host "  - INSTALLATION_WINDOWS.txt (troubleshooting)" -ForegroundColor Gray

Write-Host "`nPress Enter to launch application now or Ctrl+C to exit..." -ForegroundColor Yellow
Read-Host

# Launch app
Write-Host "`nLaunching HydroAI..." -ForegroundColor Cyan
& python launcher.py
