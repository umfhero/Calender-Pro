#!/usr/bin/env python3
"""
Calendar Pro - Build Package Script
Builds a standalone executable package for the Calendar Pro application.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def print_status(message):
    """Print status message with formatting."""
    print(f"\n{'='*60}")
    print(f"📦 {message}")
    print(f"{'='*60}")


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔧 {description}...")
    print(f"Command: {command}")

    result = subprocess.run(command, shell=True,
                            capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print("Output:", result.stdout.strip())
    else:
        print(f"❌ {description} failed!")
        print("Error:", result.stderr.strip())
        return False
    return True


def clean_previous_builds():
    """Clean up previous build artifacts."""
    print_status("Cleaning Previous Builds")

    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🗑️  Removing directory: {dir_name}")
            shutil.rmtree(dir_name)
        else:
            print(f"📁 Directory {dir_name} not found (OK)")

    # Remove .spec files
    for spec_file in Path('.').glob('*.spec'):
        print(f"🗑️  Removing spec file: {spec_file}")
        spec_file.unlink()


def check_dependencies():
    """Check if all required dependencies are installed."""
    print_status("Checking Dependencies")

    required_packages = ['customtkinter', 'Pillow', 'pyinstaller']

    for package in required_packages:
        try:
            result = subprocess.run([sys.executable, '-c', f'import {package}'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package} is installed")
            else:
                print(f"❌ {package} is not installed")
                return False
        except Exception as e:
            print(f"❌ Error checking {package}: {e}")
            return False

    return True


def install_dependencies():
    """Install dependencies from requirements.txt."""
    print_status("Installing Dependencies")

    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found!")
        return False

    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing requirements"
    )


def create_pyinstaller_spec():
    """Create a custom PyInstaller spec file for better control."""
    print_status("Creating PyInstaller Specification")

    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['calendar_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('calendar.ico', '.'),
        ('house.ico', '.'),
        ('icon.png', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CalendarPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='calendar.ico',  # Application icon
)
'''

    with open('CalendarPro.spec', 'w') as f:
        f.write(spec_content)

    print("✅ PyInstaller spec file created: CalendarPro.spec")
    return True


def build_executable():
    """Build the executable using PyInstaller."""
    print_status("Building Executable")

    # Build using the spec file for better control
    return run_command(
        "pyinstaller CalendarPro.spec --clean",
        "Building executable with PyInstaller"
    )


def create_distribution_folder():
    """Create a clean distribution folder with all necessary files."""
    print_status("Creating Distribution Package")

    dist_folder = "CalendarPro_Distribution"

    # Create distribution folder
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)
    os.makedirs(dist_folder)

    # Copy executable
    exe_source = os.path.join("dist", "CalendarPro.exe")
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, dist_folder)
        print(f"✅ Copied executable to {dist_folder}")
    else:
        print(f"❌ Executable not found at {exe_source}")
        return False

    # Copy documentation and license files
    docs_to_copy = ['README.md']
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, dist_folder)
            print(f"✅ Copied {doc}")

    # Create a simple launcher script (optional)
    launcher_content = '''@echo off
echo Starting Calendar Pro...
CalendarPro.exe
pause
'''
    with open(os.path.join(dist_folder, "Start_CalendarPro.bat"), 'w') as f:
        f.write(launcher_content)

    print(f"✅ Distribution package created in: {dist_folder}")
    return True


def create_installer_info():
    """Create installation instructions."""
    print_status("Creating Installation Instructions")

    instructions = '''# Calendar Pro - Installation Instructions

## Quick Start
1. Extract all files to a folder of your choice
2. Double-click `CalendarPro.exe` to run the application
3. Alternatively, use `Start_CalendarPro.bat` for a console window

## System Requirements
- Windows 10 or later (64-bit recommended)
- No additional software required - this is a standalone executable

## Features
- 📅 Modern calendar interface with monthly navigation
- 📝 Note management with countdown indicators  
- ⏰ Weekly timetable with module management
- 🎨 Color-coded modules and customizable rooms
- 💾 Local data storage (notes.json, timetable.json, modules.json)

## Data Storage
Your calendar data is stored locally in the same folder as the executable:
- `notes.json` - Your daily notes
- `timetable.json` - Your weekly schedule  
- `modules.json` - Your course/module information

## Troubleshooting
- If the application doesn't start, ensure you have extracted all files
- Your antivirus might flag the executable - this is normal for PyInstaller builds
- Data files are created automatically on first run

## Version Information
Built with Python and CustomTkinter
Packaged using PyInstaller

For updates and source code, visit: https://github.com/umfhero/Calender
'''

    with open('CalendarPro_Distribution/INSTALL.txt', 'w') as f:
        f.write(instructions)

    print("✅ Installation instructions created")
    return True


def main():
    """Main build process."""
    print_status("Calendar Pro - Package Builder")
    print("🚀 Starting build process for Calendar Pro...")

    # Check if we're in the right directory
    if not os.path.exists('calendar_app.py'):
        print("❌ calendar_app.py not found! Please run this script from the project directory.")
        return False

    try:
        # Step 1: Clean previous builds
        clean_previous_builds()

        # Step 2: Check dependencies
        if not check_dependencies():
            print("📦 Installing missing dependencies...")
            if not install_dependencies():
                print("❌ Failed to install dependencies!")
                return False

        # Step 3: Create PyInstaller spec
        if not create_pyinstaller_spec():
            return False

        # Step 4: Build executable
        if not build_executable():
            return False

        # Step 5: Create distribution package
        if not create_distribution_folder():
            return False

        # Step 6: Create installation instructions
        if not create_installer_info():
            return False

        print_status("Build Complete! 🎉")
        print("📁 Your packaged application is ready in: CalendarPro_Distribution/")
        print("📋 Installation instructions: CalendarPro_Distribution/INSTALL.txt")
        print("\n🎯 Next steps:")
        print("   1. Test the executable: CalendarPro_Distribution/CalendarPro.exe")
        print("   2. Create a ZIP file for distribution")
        print("   3. Share with users!")

        return True

    except Exception as e:
        print(f"❌ Build failed with error: {e}")
        return False


if __name__ == "__main__":
    success = main()

    print(f"\n{'='*60}")
    if success:
        print("🎉 BUILD SUCCESSFUL! Your Calendar Pro package is ready!")
    else:
        print("❌ BUILD FAILED! Please check the errors above.")
    print(f"{'='*60}")

    input("\nPress Enter to exit...")
