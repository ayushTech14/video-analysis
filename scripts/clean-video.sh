# 1. Unload any existing loopback device
sudo modprobe -r v4l2loopback

# 2. Kill any process using /dev/video0
sudo fuser -k /dev/video0 2>/dev/null

# 3. Remove stale device node if it still exists
sudo rm -f /dev/video0

# 4. Reboot the system to reset the device state
sudo reboot
