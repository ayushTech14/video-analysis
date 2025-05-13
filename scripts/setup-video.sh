# 1. Load v4l2loopback with correct parameters
sudo modprobe v4l2loopback devices=1 video_nr=0 card_label="VirtualCam" exclusive_caps=1 max_width=1280 max_height=720

# 2. Check device node
ls -al /dev/video*

# 3. Add user to video group (only needed once)
sudo usermod -aG video $USER

# 4. Set device permissions (optional if user is in video group)
sudo chmod 666 /dev/video0
