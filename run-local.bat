@echo off
REM Run Interior Design System locally for development (Windows)
REM Prerequisites: Python 3.11+, Blender 4.0+ (optional)

echo === Interior Design System - Local Development ===

cd /d "%~dp0"

REM ============================================================================
REM CHECK DEPENDENCIES
REM ============================================================================

echo Checking dependencies...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is required
    exit /b 1
)

where blender >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('where blender') do set BLENDER_PATH=%%i
    echo Blender found: %BLENDER_PATH%
) else (
    echo Warning: Blender not found. Running in mock mode.
    set USE_MOCK_BLENDER=true
)

REM ============================================================================
REM SETUP DIRECTORIES
REM ============================================================================

echo Setting up directories...

if not exist "output" mkdir output
if not exist "scenes" mkdir scenes
if not exist "uploads" mkdir uploads

REM ============================================================================
REM SETUP PYTHON ENVIRONMENT
REM ============================================================================

echo Setting up Python environment...

cd backend

if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install --upgrade pip -q
pip install -r requirements.txt -q

REM ============================================================================
REM SET ENVIRONMENT
REM ============================================================================

set BLENDER_SCRIPTS_DIR=%~dp0blender\scripts
set OUTPUT_DIR=%~dp0output
set SCENES_DIR=%~dp0scenes
set UPLOADS_DIR=%~dp0uploads
set ASSETS_DIR=%~dp0blender\assets

REM Load .env if exists
if exist "..\.env" (
    for /f "usebackq tokens=1,* delims==" %%a in ("..\.env") do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" set "%%a=%%b"
    )
)

REM ============================================================================
REM START SERVER
REM ============================================================================

echo.
echo Starting backend server...
echo.
echo Backend: http://localhost:8000
echo Frontend: Open frontend\index.html in browser
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
