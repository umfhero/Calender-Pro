@echo off
echo ============================================
echo    Calendar Pro - Simple Build Script
echo ============================================
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

echo Cleaned previous builds...
echo.

REM Create simple PyInstaller command
echo Building Calendar Pro executable...
echo This may take a few minutes...
echo.

pyinstaller --onefile --windowed --name "CalendarPro" --icon "calendar.ico" --add-data "calendar.ico;." --add-data "house.ico;." --add-data "icon.png;." calendar_app.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo           BUILD SUCCESSFUL!
    echo ============================================
    echo.
    echo Your executable is ready: dist\CalendarPro.exe
    echo.
    if exist "dist\CalendarPro.exe" (
        echo File size: 
        dir "dist\CalendarPro.exe" | find "CalendarPro.exe"
        echo.
        echo You can now run: dist\CalendarPro.exe
    )
) else (
    echo.
    echo ============================================
    echo            BUILD FAILED!
    echo ============================================
    echo.
    echo Check the output above for errors.
)

echo.
pause
