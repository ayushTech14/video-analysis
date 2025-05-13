#!/bin/bash

# -------------------------
# Usage
# -------------------------
# ./launch-validation.sh <user> <file> [fps] [timer]
# Example:
# ./launch-validation.sh mohan face.mp4 15 1000

# -------------------------
# Input parameters
# -------------------------
USER_NAME=$1
VIDEO_FILE=$2
FPS=${3:-15}           # Default FPS is 15
TIMER=${4:-1000}       # Default TIMER is 1000 ms

SRC_PATH="/home/ubuntu/$VIDEO_FILE"
DEST_DIR="/home/ubuntu/vid"
DEST_PATH="$DEST_DIR/$VIDEO_FILE"

# -------------------------
# Validate input
# -------------------------
if [[ -z "$USER_NAME" || -z "$VIDEO_FILE" ]]; then
  echo "[ERROR] Usage: $0 <user> <file> [fps] [timer]"
  exit 1
fi

# -------------------------
# Move video if in /home/ubuntu
# -------------------------
if [[ -f "$SRC_PATH" ]]; then
  echo "[INFO] Moving $SRC_PATH to $DEST_DIR"
  sudo mkdir -p "$DEST_DIR"
  sudo mv "$SRC_PATH" "$DEST_PATH"
elif [[ -f "$DEST_PATH" ]]; then
  echo "[INFO] File already in $DEST_DIR"
else
  echo "[ERROR] File not found at $SRC_PATH or $DEST_PATH"
  exit 1
fi

# -------------------------
# Step 1: Start Podman container in background
# -------------------------
echo "[INFO] Launching driver detection container with timer=$TIMER ms..."
podman run --rm --net=host \
  --device /dev/video0:/dev/video0 \
  -v /home/ubuntu/trained_knn_model.clf:/home/app/trained_knn_model.clf:Z \
  --user root \
  quay.io/nikesh_sar/driver-detection-arm64:tag \
  --timer "$TIMER" &
PODMAN_PID=$!
echo "[INFO] Waiting 10 seconds before hitting server"
sleep 10
# -------------------------
# Step 2: Ping localhost:5000 once (optional info)
# -------------------------
echo "[INFO] Sending browser-style request to wake server..."
curl -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" http://13.59.191.199:5000/ --silent || echo "[WARN] Server did not respond to refresh attempt"
echo "[INFO] Waiting 5 seconds before starting Python script..."
sleep 5

echo "[INFO] Running get-data.py for user=$USER_NAME, file=$DEST_PATH, fps=$FPS"
sudo python3 /home/ubuntu/get-data.py --user "$USER_NAME" --file "$DEST_PATH" --fps "$FPS" --device /dev/video0 &

# -------------------------
# Wait for Podman to complete
# -------------------------
wait $PODMAN_PID
