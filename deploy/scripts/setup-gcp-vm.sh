#!/bin/bash
# GCP GPU VM Setup Script for Interior Design System
# This script sets up a GCP VM with NVIDIA T4 GPU, Blender, and the backend

set -e

echo "=== Interior Design System - GCP VM Setup ==="

# ============================================================================
# VARIABLES
# ============================================================================

PROJECT_DIR="/app/interior-design"
BLENDER_VERSION="4.0.2"
BLENDER_URL="https://mirror.clarkson.edu/blender/release/Blender4.0/blender-${BLENDER_VERSION}-linux-x64.tar.xz"

# ============================================================================
# SYSTEM UPDATES
# ============================================================================

echo ">>> Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# ============================================================================
# NVIDIA DRIVERS (for T4 GPU)
# ============================================================================

echo ">>> Installing NVIDIA drivers..."

# Check if NVIDIA drivers are already installed
if ! command -v nvidia-smi &> /dev/null; then
    # Install NVIDIA driver
    sudo apt-get install -y linux-headers-$(uname -r)

    # Add NVIDIA repository
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
    wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
    sudo dpkg -i cuda-keyring_1.0-1_all.deb
    sudo apt-get update

    # Install CUDA toolkit and drivers
    sudo apt-get install -y cuda-drivers

    echo ">>> NVIDIA drivers installed. A reboot may be required."
else
    echo ">>> NVIDIA drivers already installed."
    nvidia-smi
fi

# ============================================================================
# PYTHON AND DEPENDENCIES
# ============================================================================

echo ">>> Installing Python and dependencies..."

sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    wget \
    curl \
    nginx \
    supervisor \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    xvfb

# ============================================================================
# BLENDER INSTALLATION
# ============================================================================

echo ">>> Installing Blender ${BLENDER_VERSION}..."

BLENDER_DIR="/opt/blender"

if [ ! -d "$BLENDER_DIR" ]; then
    cd /tmp
    wget -O blender.tar.xz "$BLENDER_URL"
    sudo mkdir -p "$BLENDER_DIR"
    sudo tar -xf blender.tar.xz -C "$BLENDER_DIR" --strip-components=1
    rm blender.tar.xz

    # Create symlink
    sudo ln -sf "${BLENDER_DIR}/blender" /usr/local/bin/blender

    echo ">>> Blender installed at ${BLENDER_DIR}"
else
    echo ">>> Blender already installed."
fi

# Verify Blender
blender --version

# ============================================================================
# PROJECT SETUP
# ============================================================================

echo ">>> Setting up project directory..."

sudo mkdir -p "$PROJECT_DIR"
sudo chown -R $(whoami):$(whoami) "$PROJECT_DIR"

# Clone or copy project files
# In production, you would clone from your repository:
# git clone https://github.com/your-org/interior-design.git "$PROJECT_DIR"

# For now, we'll create the directory structure
mkdir -p "$PROJECT_DIR"/{backend,blender,frontend,output,scenes,uploads}

# ============================================================================
# PYTHON VIRTUAL ENVIRONMENT
# ============================================================================

echo ">>> Setting up Python virtual environment..."

cd "$PROJECT_DIR/backend"

python3.11 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

deactivate

# ============================================================================
# NGINX CONFIGURATION
# ============================================================================

echo ">>> Configuring Nginx..."

sudo tee /etc/nginx/sites-available/interior-design << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend static files
    location / {
        root /app/interior-design/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;

        # Allow large uploads
        client_max_body_size 50M;
    }

    # Serve generated models
    location /models {
        alias /app/interior-design/output;
        add_header Access-Control-Allow-Origin *;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/interior-design /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# ============================================================================
# SUPERVISOR CONFIGURATION
# ============================================================================

echo ">>> Configuring Supervisor for backend service..."

sudo tee /etc/supervisor/conf.d/interior-design.conf << 'EOF'
[program:interior-design-backend]
command=/app/interior-design/backend/venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
directory=/app/interior-design/backend
user=root
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/interior-design/backend.err.log
stdout_logfile=/var/log/interior-design/backend.out.log
environment=
    GEMINI_API_KEY="%(ENV_GEMINI_API_KEY)s",
    BLENDER_PATH="/usr/local/bin/blender",
    BLENDER_SCRIPTS_DIR="/app/interior-design/blender/scripts",
    OUTPUT_DIR="/app/interior-design/output",
    SCENES_DIR="/app/interior-design/scenes",
    UPLOADS_DIR="/app/interior-design/uploads",
    ASSETS_DIR="/app/interior-design/blender/assets"
EOF

sudo mkdir -p /var/log/interior-design
sudo supervisorctl reread
sudo supervisorctl update

# ============================================================================
# FIREWALL CONFIGURATION
# ============================================================================

echo ">>> Configuring firewall..."

sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw --force enable

# ============================================================================
# GENERATE PLACEHOLDER ASSETS
# ============================================================================

echo ">>> Generating placeholder assets with Blender..."

cd "$PROJECT_DIR"

# Run Blender headless to generate assets
xvfb-run -a blender --background --python blender/scripts/generate_placeholder_assets.py || true

# ============================================================================
# DONE
# ============================================================================

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Copy your project files to ${PROJECT_DIR}"
echo "2. Set GEMINI_API_KEY environment variable"
echo "3. Start the service: sudo supervisorctl start interior-design-backend"
echo "4. Access the application at http://<VM_IP>/"
echo ""
