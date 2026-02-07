@echo off
echo Building GitHub Viewer executable in virtual environment...

REM Set venv path
set VENV_PATH=env

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create venv if it doesn't exist
if not exist "%VENV_PATH%" (
    echo Creating virtual environment in %VENV_PATH%...
    python -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call "%VENV_PATH%\Scripts\activate.bat"

REM Upgrade pip
python -m pip install --upgrade pip

REM Install required dependencies
echo Installing required dependencies...
pip install keyring requests GitPython nuitka
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if icon file exists
if not exist "assets\icon.ico" (
    echo Warning: Icon file assets\icon.ico not found, building without icon
    set ICON_OPTION=
) else (
    set ICON_OPTION=--windows-icon-from-ico=assets/icon.ico
)

REM Create dist directory if it doesn't exist
if not exist "dist" mkdir dist

REM Clean previous builds
if exist "dist\github_viewer.exe" del "dist\github_viewer.exe"

echo Starting compilation with Nuitka...
python -m nuitka ^
    --onefile ^
    %ICON_OPTION% ^
    --output-dir=dist ^
    --output-filename=github_viewer.exe ^
    --remove-output ^
    --assume-yes-for-downloads ^
    --enable-plugin=anti-bloat ^
    --include-module=keyring ^
    --include-module=requests ^
    --include-module=git ^
    src/main.py

if errorlevel 1 (
    echo Error: Build failed
    pause
    exit /b 1
)

echo Build completed successfully!
echo Executable location: dist\github_viewer.exe

REM Check if executable was created
if exist "dist\github_viewer.exe" (
    echo File size: 
    dir "dist\github_viewer.exe" | findstr github_viewer.exe
) else (
    echo Warning: Executable not found in dist directory
)

REM Deactivate virtual environment
deactivate

pause
