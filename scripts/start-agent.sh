#!/bin/bash

# Auto Analytics AI Agent Startup Script
# This script starts the AI agent system (ADK) on port 8000

set -e

# Get the workspace root directory
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORKSPACE_ROOT"

echo "🤖 Starting Auto Analytics AI Agent..."
echo "📁 Workspace: $WORKSPACE_ROOT"
echo "🔧 Using Google ADK (Agent Development Kit)"
echo "🧠 Model: Gemini 2.5 Flash"
echo "🌐 Port: 8000"
echo ""

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "📦 Installing dependencies with uv..."
    uv sync
    echo ""
    
    echo "🚀 Starting ADK web interface..."
    echo "💡 The agent will generate HTML reports to: $WORKSPACE_ROOT/reports/"
    echo "💡 Access the agent at: http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the agent"
    echo "=================================================================================="
    
    # Start the ADK web interface
    uv run adk web --port 8000
else
    echo "❌ Error: uv is not installed"
    echo "Please install uv first: https://docs.astral.sh/uv/"
    exit 1
fi