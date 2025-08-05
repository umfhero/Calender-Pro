# Calendar Pro - PowerShell Build Script
# This script builds a standalone executable package for Calendar Pro

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "    Calendar Pro - Package Builder" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "calendar_app.py")) {
    Write-Host "❌ calendar_app.py not found!" -ForegroundColor Red
    Write-Host "Please run this script from the Calendar project directory." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🚀 Starting build process..." -ForegroundColor Green
Write-Host ""

# Run the Python build script
try {
    python build_package.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 Package build completed successfully!" -ForegroundColor Green
        Write-Host "📁 Check the CalendarPro_Distribution folder for your packaged app" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "❌ Build failed. Please check the output above for errors." -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error running build script: $_" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
