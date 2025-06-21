#!/bin/bash

# Auto Analytics FastAPI Report Server Startup Script
# This script starts the independent FastAPI server on port 9000

set -e

# Get the workspace root directory
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FASTAPI_DIR="$WORKSPACE_ROOT/fastapi-server"
REPORTS_DIR="$WORKSPACE_ROOT/reports"

echo "🌐 Starting Auto Analytics FastAPI Report Server..."
echo "📁 Workspace: $WORKSPACE_ROOT"
echo "📊 FastAPI Server Directory: $FASTAPI_DIR"
echo "📁 Reports Directory: $REPORTS_DIR"
echo "🌐 Port: 9000"
echo ""

# Ensure reports directory exists
mkdir -p "$REPORTS_DIR"

# Change to FastAPI directory
cd "$FASTAPI_DIR"

# Check if we're in a virtual environment or if pip is available
if [[ "$VIRTUAL_ENV" != "" ]] || command -v pip &> /dev/null; then
    echo "📦 Installing FastAPI dependencies..."
    pip install -r requirements.txt
    echo ""
    
    echo "🚀 Starting FastAPI Report Server..."
    echo "💡 The server will display reports from: $REPORTS_DIR"
    echo "💡 Main interface: http://localhost:9000"
    echo "💡 API documentation: http://localhost:9000/api/docs"
    echo "💡 Report list API: http://localhost:9000/api/reports"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "=================================================================================="
    
    # Start the FastAPI server
    python main.py --host localhost --port 9000 --reports-dir "$REPORTS_DIR"
    
elif command -v uv &> /dev/null; then
    echo "📦 Installing dependencies with uv..."
    # Create a simple pyproject.toml for uv
    if [ ! -f "pyproject.toml" ]; then
        cat > pyproject.toml << EOF
[project]
name = "fastapi-report-server"
version = "0.1.0"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "aiofiles>=24.1.0",
    "jinja2>=3.1.0",
    "python-multipart>=0.0.6"
]
requires-python = ">=3.11"
EOF
    fi
    
    uv sync
    echo ""
    
    echo "🚀 Starting FastAPI Report Server..."
    echo "💡 The server will display reports from: $REPORTS_DIR"
    echo "💡 Main interface: http://localhost:9000"
    echo "💡 API documentation: http://localhost:9000/api/docs"
    echo "💡 Report list API: http://localhost:9000/api/reports"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "=================================================================================="
    
    # Start the FastAPI server
    uv run python main.py --host localhost --port 9000 --reports-dir "$REPORTS_DIR"
    
else
    echo "❌ Error: Neither pip nor uv is available"
    echo "Please install pip or uv, or activate a Python virtual environment"
    exit 1
fi