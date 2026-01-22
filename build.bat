@echo off
setlocal

echo APK Resign GUI - Build Script
echo =============================

REM Check if running from the correct directory
if not exist "main.py" (
    echo Error: main.py not found in current directory!
    echo Please run this script from the project root.
    pause
    exit /b 1
)

echo.
echo Building APK Resign GUI...
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Activated virtual environment
)

REM Install dependencies if not already installed
python -c "import PyInstaller" 2>nul || (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Run the build script
python build.py

echo.
echo Build process completed!
echo The executable can be found in the 'dist' folder.
echo.

pause