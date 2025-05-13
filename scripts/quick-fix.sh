#!/bin/bash

set -e

echo "[1] Unloading existing v4l2loopback module..."
sudo modprobe -r v4l2loopback || echo "Module not loaded or already removed."

echo "[2] Killing any processes using /dev/video0..."
sudo fuser -k /dev/video0 2>/dev/null || echo "No process was using /dev/video0."

echo "[3] Removing stale /dev/video0 node (if exists)..."
sudo rm -f /dev/video0

echo "[4] Loading v4l2loopback with your parameters..."
sudo modprobe v4l2loopback devices=1 video_nr=0 card_label="VirtualCam" exclusive_caps=1

echo "[5] Listing virtual video devices..."
ls -al /dev/video*

echo "[6] Adding user '$USER' to video group (only needed once)..."
sudo usermod -aG video "$USER"

echo "[7] Setting read/write permissions on /dev/video0..."
sudo chmod 666 /dev/video0
ls -al /dev/video*

echo "[✅] Virtual camera setup complete."
