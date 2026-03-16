@echo off
REM FlowSync Python - Windows Startup Script

echo ============================================================
echo FlowSync Python - Setup and Start
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from python.org
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo [2/5] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
) else (
    echo.
    echo [2/5] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file with your database settings!
    echo Press any key to open .env in notepad...
    pause
    notepad .env
)

REM Initialize database (optional)
echo.
echo [5/5] Do you want to initialize the database? (y/n)
set /p init_db="Initialize database tables? (y/n): "
if /i "%init_db%"=="y" (
    echo Initializing database...
    python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
    if errorlevel 1 (
        echo WARNING: Database initialization failed. Make sure PostgreSQL is running.
    ) else (
        echo Database initialized successfully!
    )
)

echo.
echo ============================================================
echo Starting FlowSync Python Server...
echo ============================================================
echo.
echo Server will start on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/api/health
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the server
python run.py

pause

