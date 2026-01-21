#!/bin/bash
# Run Interior Design System locally for development
# Prerequisites: Python 3.11+, Blender 4.0+

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Interior Design System - Local Development ==="

# ============================================================================
# CHECK DEPENDENCIES
# ============================================================================

echo ">>> Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Check Blender (optional for mock mode)
if command -v blender &> /dev/null; then
    echo "Blender found: $(blender --version | head -1)"
    export BLENDER_PATH=$(which blender)
else
    echo "Warning: Blender not found. Running in mock mode."
    export USE_MOCK_BLENDER=true
fi

# ============================================================================
# SETUP DIRECTORIES
# ============================================================================

echo ">>> Setting up directories..."

mkdir -p output scenes uploads

# ============================================================================
# SETUP PYTHON ENVIRONMENT
# ============================================================================

echo ">>> Setting up Python environment..."

cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

# ============================================================================
# LOAD ENVIRONMENT
# ============================================================================

if [ -f "../.env" ]; then
    echo ">>> Loading environment from .env"
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# Set default paths
export BLENDER_SCRIPTS_DIR="${BLENDER_SCRIPTS_DIR:-$SCRIPT_DIR/blender/scripts}"
export OUTPUT_DIR="${OUTPUT_DIR:-$SCRIPT_DIR/output}"
export SCENES_DIR="${SCENES_DIR:-$SCRIPT_DIR/scenes}"
export UPLOADS_DIR="${UPLOADS_DIR:-$SCRIPT_DIR/uploads}"
export ASSETS_DIR="${ASSETS_DIR:-$SCRIPT_DIR/blender/assets}"

# ============================================================================
# START SERVERS
# ============================================================================

echo ""
echo ">>> Starting backend server..."
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: Open frontend/index.html in browser"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
