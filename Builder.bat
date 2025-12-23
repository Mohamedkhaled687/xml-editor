@echo off
echo ==========================================
echo SocialX Build Script
echo ==========================================
echo [1/2] Checking and Installing Dependencies...
:: Install required packages
pip install PySide6 networkx matplotlib numpy colorama pyinstaller
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install dependencies. Please check your internet connection or python installation.
    pause
    exit /b %errorlevel%
)
echo.
echo [2/2] Building Executable with PyInstaller...
echo.
:: Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec
:: Run PyInstaller
:: --onefile: Create a single executable file
:: --name "SocialX_v12": Name the output file
:: --clean: Clean PyInstaller cache
:: --icon "icon.ico": Add application icon
:: --add-data "icon.ico;.": Bundle icon file inside the exe
:: Note: specific imports handled by PyInstaller analysis
pyinstaller --name "SocialX" --onefile --clean --icon "assets\icon.ico" --add-data "assets\icon.ico;." main.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PyInstaller failed to build the executable.
    pause
    exit /b %errorlevel%
)
echo.
echo ==========================================
echo Build Successful!
echo Executable located in: dist\SocialX.exe
echo ==========================================
pause
