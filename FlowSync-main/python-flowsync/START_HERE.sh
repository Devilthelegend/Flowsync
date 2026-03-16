#!/bin/bash
# FlowSync Python - Linux/Mac Startup Script

echo "============================================================"
echo "FlowSync Python - Setup and Start"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo "[1/5] Checking Python version..."
python3 --version

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "[2/5] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully!"
else
    echo ""
    echo "[2/5] Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "[3/5] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "[4/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: .env file not found!"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit .env file with your database settings!"
    echo "Opening .env in default editor..."
    ${EDITOR:-nano} .env
fi

# Initialize database (optional)
echo ""
read -p "[5/5] Initialize database tables? (y/n): " init_db
if [ "$init_db" = "y" ] || [ "$init_db" = "Y" ]; then
    echo "Initializing database..."
    python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
    if [ $? -ne 0 ]; then
        echo "WARNING: Database initialization failed. Make sure PostgreSQL is running."
    else
        echo "Database initialized successfully!"
    fi
fi

echo ""
echo "============================================================"
echo "Starting FlowSync Python Server..."
echo "============================================================"
echo ""
echo "Server will start on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Start the server
python run.py

