#!/usr/bin/env python3
"""
Simple Calendar Pro Builder
A streamlined build script that's less prone to hanging.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def print_header(message):
    print(f"\n{'='*50}")
    print(f"📦 {message}")
    print(f"{'='*50}")


def clean_builds():
    """Clean previous build artifacts."""
    print_header("Cleaning Previous Builds")

    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🗑️  Removing: {dir_name}")
            shutil.rmtree(dir_name)

    # Remove spec files
    for spec_file in Path('.').glob('*.spec'):
        print(f"🗑️  Removing: {spec_file}")
        spec_file.unlink()

    print("✅ Cleanup completed!")


def build_simple():
    """Build using simple PyInstaller command."""
    print_header("Building Calendar Pro")

    # Simple PyInstaller command - less likely to hang
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'CalendarPro',
        '--icon', 'calendar.ico',
        '--add-data', 'calendar.ico;.',
        '--add-data', 'house.ico;.',
        '--add-data', 'icon.png;.',
        'calendar_app.py'
    ]

    print("🔧 Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    print("\n⏳ This may take 2-5 minutes, please wait...")

    try:
        # Run with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Print output in real-time
        for line in process.stdout:
            if line.strip():
                print(f"   {line.strip()}")

        process.wait()

        if process.returncode == 0:
            print("\n✅ Build completed successfully!")

            # Check if executable exists
            exe_path = Path("dist/CalendarPro.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📁 Executable created: {exe_path}")
                print(f"📊 File size: {size_mb:.1f} MB")

                # Create a simple distribution folder
                create_distribution()
                return True
            else:
                print("❌ Executable file not found!")
                return False
        else:
            print(f"❌ Build failed with return code: {process.returncode}")
            return False

    except Exception as e:
        print(f"❌ Error during build: {e}")
        return False


def create_distribution():
    """Create a simple distribution folder."""
    print_header("Creating Distribution")

    dist_folder = "CalendarPro_Package"

    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)
    os.makedirs(dist_folder)

    # Copy executable
    exe_source = "dist/CalendarPro.exe"
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, dist_folder)
        print(f"✅ Copied executable to {dist_folder}/")

    # Copy readme
    if os.path.exists("README.md"):
        shutil.copy2("README.md", dist_folder)
        print("✅ Copied README.md")

    # Create simple instructions
    instructions = """# Calendar Pro - Standalone Application

## How to Run
1. Double-click CalendarPro.exe to start the application
2. No installation required - this is a portable application
3. Your data will be saved in the same folder as the executable

## Features
- Monthly calendar view with note management
- Weekly timetable with module scheduling
- Color-coded modules and room management
- Local data storage (JSON files)

## System Requirements
- Windows 10 or later
- No additional software required

## Data Files
The application creates these files automatically:
- notes.json (your calendar notes)
- timetable.json (your weekly schedule)
- modules.json (your course modules)

## Troubleshooting
- If Windows shows a security warning, click "More info" then "Run anyway"
- This is normal for PyInstaller-built applications
- Your antivirus may scan the file - this is also normal

Enjoy using Calendar Pro!
"""

    with open(f"{dist_folder}/README.txt", 'w') as f:
        f.write(instructions)

    print(f"✅ Created distribution package: {dist_folder}/")


def main():
    """Main build process."""
    print_header("Calendar Pro - Simple Builder")
    print("🚀 Starting streamlined build process...")

    # Check if we're in the right directory
    if not os.path.exists('calendar_app.py'):
        print("❌ calendar_app.py not found!")
        print("Please run this script from the Calendar project directory.")
        return False

    try:
        # Step 1: Clean
        clean_builds()

        # Step 2: Build
        if build_simple():
            print_header("BUILD SUCCESSFUL! 🎉")
            print("📁 Your app is ready in: CalendarPro_Package/")
            print("🎯 Just double-click CalendarPro.exe to run!")
            return True
        else:
            print_header("BUILD FAILED! ❌")
            print("Check the output above for errors.")
            return False

    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()

    print(f"\n{'='*50}")
    if success:
        print("🎉 BUILD COMPLETE!")
    else:
        print("❌ BUILD FAILED!")
    print(f"{'='*50}")

    input("\nPress Enter to exit...")
