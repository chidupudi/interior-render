#!/bin/bash
# Create GCP GPU VM for Interior Design System
# Prerequisites: gcloud CLI installed and authenticated

set -e

# ============================================================================
# CONFIGURATION - Modify these values
# ============================================================================

PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
ZONE="us-central1-a"
INSTANCE_NAME="interior-design-gpu"
MACHINE_TYPE="n1-standard-4"
GPU_TYPE="nvidia-tesla-t4"
GPU_COUNT=1
BOOT_DISK_SIZE="100GB"
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"

# ============================================================================
# CREATE FIREWALL RULES
# ============================================================================

echo ">>> Creating firewall rules..."

# Allow HTTP traffic
gcloud compute firewall-rules create allow-http \
    --project="$PROJECT_ID" \
    --allow=tcp:80 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server \
    --description="Allow HTTP traffic" \
    2>/dev/null || echo "Firewall rule 'allow-http' already exists"

# Allow HTTPS traffic
gcloud compute firewall-rules create allow-https \
    --project="$PROJECT_ID" \
    --allow=tcp:443 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=https-server \
    --description="Allow HTTPS traffic" \
    2>/dev/null || echo "Firewall rule 'allow-https' already exists"

# ============================================================================
# CREATE GPU VM INSTANCE
# ============================================================================

echo ">>> Creating GPU VM instance: $INSTANCE_NAME..."

gcloud compute instances create "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --zone="$ZONE" \
    --machine-type="$MACHINE_TYPE" \
    --accelerator="type=$GPU_TYPE,count=$GPU_COUNT" \
    --maintenance-policy=TERMINATE \
    --provisioning-model=STANDARD \
    --boot-disk-size="$BOOT_DISK_SIZE" \
    --boot-disk-type=pd-ssd \
    --image-family="$IMAGE_FAMILY" \
    --image-project="$IMAGE_PROJECT" \
    --tags=http-server,https-server \
    --metadata=enable-oslogin=TRUE \
    --scopes=https://www.googleapis.com/auth/cloud-platform

# ============================================================================
# WAIT FOR INSTANCE TO BE READY
# ============================================================================

echo ">>> Waiting for instance to be ready..."
sleep 30

# ============================================================================
# GET INSTANCE IP
# ============================================================================

EXTERNAL_IP=$(gcloud compute instances describe "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --zone="$ZONE" \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo ""
echo "=== VM Created Successfully ==="
echo ""
echo "Instance Name: $INSTANCE_NAME"
echo "External IP: $EXTERNAL_IP"
echo "Zone: $ZONE"
echo ""
echo "Next steps:"
echo "1. SSH into the VM:"
echo "   gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID"
echo ""
echo "2. Run the setup script on the VM:"
echo "   sudo bash /path/to/setup-gcp-vm.sh"
echo ""
echo "3. Set environment variables:"
echo "   export GEMINI_API_KEY='your-api-key'"
echo ""
echo "4. Access the application:"
echo "   http://$EXTERNAL_IP/"
echo ""
