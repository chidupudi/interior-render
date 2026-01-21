# Interior Design System - Docker Image
# Multi-stage build with Blender and Python backend

# ============================================================================
# Stage 1: Blender + Python Base
# ============================================================================

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 AS base

ENV DEBIAN_FRONTEND=noninteractive
ENV BLENDER_VERSION=4.0.2
ENV BLENDER_URL=https://mirror.clarkson.edu/blender/release/Blender4.0/blender-${BLENDER_VERSION}-linux-x64.tar.xz

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    wget \
    curl \
    xvfb \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Install Blender
RUN cd /tmp && \
    wget -O blender.tar.xz "$BLENDER_URL" && \
    mkdir -p /opt/blender && \
    tar -xf blender.tar.xz -C /opt/blender --strip-components=1 && \
    rm blender.tar.xz && \
    ln -sf /opt/blender/blender /usr/local/bin/blender

# ============================================================================
# Stage 2: Application
# ============================================================================

FROM base AS app

WORKDIR /app

# Create directories
RUN mkdir -p /app/{backend,blender,frontend,output,scenes,uploads}

# Copy backend
COPY backend/requirements.txt /app/backend/
RUN python3.11 -m venv /app/backend/venv && \
    /app/backend/venv/bin/pip install --upgrade pip && \
    /app/backend/venv/bin/pip install -r /app/backend/requirements.txt

COPY backend/ /app/backend/

# Copy Blender scripts and assets
COPY blender/ /app/blender/

# Copy frontend
COPY frontend/ /app/frontend/

# Environment variables
ENV GEMINI_API_KEY=""
ENV BLENDER_PATH=/usr/local/bin/blender
ENV BLENDER_SCRIPTS_DIR=/app/blender/scripts
ENV OUTPUT_DIR=/app/output
ENV SCENES_DIR=/app/scenes
ENV UPLOADS_DIR=/app/uploads
ENV ASSETS_DIR=/app/blender/assets

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start script
COPY deploy/config/docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/app/backend/venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
