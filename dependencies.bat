@echo off
setlocal

echo Cleaning up previous virtual environment (if any)...
if exist venv (
    rmdir /s /q venv
    echo Old virtual environment removed.
)

echo Setting up dependencies...

:: Check if python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python 3.9 or higher and try again.
    exit /b 1
)

:: Create a new virtual environment
echo Creating a new virtual environment...
python -m venv venv

:: Upgrade pip to the latest version
echo Upgrading pip...
call venv\Scripts\python.exe -m pip install --upgrade pip

:: Install dependencies from requirements.txt with progress bar
echo Installing dependencies...
echo This may take a few minutes...
call venv\Scripts\pip.exe install -r requirements.txt --progress-bar on

echo.
echo Dependencies installed successfully!
echo.
echo To activate the virtual environment, run:
echo     For Command Prompt: venv\Scripts\activate.bat
echo     For PowerShell: venv\Scripts\Activate.ps1
echo.
echo If you get a security error, run the following command first:
echo Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser