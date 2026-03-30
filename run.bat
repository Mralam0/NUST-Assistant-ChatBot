@echo off
setlocal
cd /d "%~dp0"

title NUST Admission Assistant

set "RUNTIME_DIR=.runtime"
set "VENV_DIR=%RUNTIME_DIR%\venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "SETUP_MARKER=%RUNTIME_DIR%\.offline_ready"
set "PYTHON_BOOTSTRAP="

echo ============================================
echo     NUST Admission Assistant
echo ============================================
echo.

py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_BOOTSTRAP=py -3"
)

if not defined PYTHON_BOOTSTRAP (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_BOOTSTRAP=python"
    )
)

if not defined PYTHON_BOOTSTRAP (
    echo [ERROR] Python 3 is not installed or not available in PATH.
    echo Install Python on this device, then run this script again.
    pause
    exit /b 1
)

if exist "%PYTHON_EXE%" if exist "%SETUP_MARKER%" (
    echo [1/2] Existing local environment detected for this device.
    goto verify_and_start
)

echo [1/3] Preparing local runtime for this device...
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"

if not exist "%PYTHON_EXE%" (
    echo Creating device-local virtual environment...
    %PYTHON_BOOTSTRAP% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create the local environment.
        pause
        exit /b 1
    )
) else (
    echo Local runtime folder found. Completing setup...
)

echo.
echo [2/3] Installing required packages...
"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies.
    echo First-time setup on a new device requires internet access.
    echo After setup completes once on that device, later runs can work offline.
    pause
    exit /b 1
)

echo ready> "%SETUP_MARKER%"
if errorlevel 1 (
    echo [ERROR] Failed to write setup marker.
    pause
    exit /b 1
)

echo.
echo [3/3] Local environment setup completed for offline reuse.

:verify_and_start
"%PYTHON_EXE%" -c "import fastapi, uvicorn, faiss, numpy, sklearn, jinja2" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Local environment exists but is incomplete.
    echo Reconnect to the internet once on this device and run again to repair setup.
    pause
    exit /b 1
)

echo.
echo [2/2] Starting chatbot server...
echo.
echo ============================================
echo   Chatbot is running at: http://localhost:8000
echo   Local device runtime: %VENV_DIR%
echo   If setup already happened on this device, internet is not required
echo   Press Ctrl+C to stop the server
echo ============================================
echo.

cd app
..\%PYTHON_EXE% -m uvicorn main:app --host 0.0.0.0 --port 8000

echo.
echo Server stopped.
pause
