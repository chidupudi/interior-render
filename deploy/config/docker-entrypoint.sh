#!/bin/bash
set -e

echo "Starting Interior Design System..."

# Create directories if they don't exist
mkdir -p /app/{output,scenes,uploads}

# Generate placeholder assets if not present
if [ ! -d "/app/blender/assets/models/doors" ]; then
    echo "Generating placeholder assets..."
    xvfb-run -a blender --background --python /app/blender/scripts/generate_placeholder_assets.py || true
fi

# Start the application
cd /app/backend
exec "$@"
