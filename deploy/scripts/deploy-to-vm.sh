#!/bin/bash
# Deploy Interior Design System to GCP VM
# Usage: ./deploy-to-vm.sh [INSTANCE_NAME] [ZONE]

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
INSTANCE_NAME="${1:-interior-design-gpu}"
ZONE="${2:-us-central1-a}"
REMOTE_DIR="/app/interior-design"
LOCAL_DIR="$(dirname "$0")/../.."

# ============================================================================
# PACKAGE PROJECT
# ============================================================================

echo ">>> Packaging project files..."

cd "$LOCAL_DIR"

# Create deployment package (excluding unnecessary files)
tar --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='*.log' \
    --exclude='output/*' \
    --exclude='scenes/*' \
    --exclude='uploads/*' \
    -czvf /tmp/interior-design-deploy.tar.gz .

# ============================================================================
# UPLOAD TO VM
# ============================================================================

echo ">>> Uploading to VM: $INSTANCE_NAME..."

# Copy package to VM
gcloud compute scp /tmp/interior-design-deploy.tar.gz \
    "$INSTANCE_NAME":~/interior-design-deploy.tar.gz \
    --zone="$ZONE" \
    --project="$PROJECT_ID"

# ============================================================================
# EXTRACT AND SETUP ON VM
# ============================================================================

echo ">>> Extracting and setting up on VM..."

gcloud compute ssh "$INSTANCE_NAME" \
    --zone="$ZONE" \
    --project="$PROJECT_ID" \
    --command="
        sudo mkdir -p $REMOTE_DIR
        sudo tar -xzf ~/interior-design-deploy.tar.gz -C $REMOTE_DIR
        sudo chown -R \$(whoami):\$(whoami) $REMOTE_DIR

        # Create required directories
        mkdir -p $REMOTE_DIR/{output,scenes,uploads}

        # Install Python dependencies
        cd $REMOTE_DIR/backend
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        deactivate

        # Restart backend service
        sudo supervisorctl restart interior-design-backend || true

        echo 'Deployment complete!'
    "

# ============================================================================
# CLEANUP
# ============================================================================

rm /tmp/interior-design-deploy.tar.gz

# ============================================================================
# GET VM IP
# ============================================================================

EXTERNAL_IP=$(gcloud compute instances describe "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --zone="$ZONE" \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Application URL: http://$EXTERNAL_IP/"
echo ""
