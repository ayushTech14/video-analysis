import socket
import threading
import time
import argparse
import subprocess
import os
import json
from datetime import datetime

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', default="guest", help="Expected username")
parser.add_argument('-f', '--file', default="face.mp4", help="Video file name")
parser.add_argument('-fps', '--fps', default="60", help="Frames per second")
parser.add_argument('--device', default="/dev/video0", help="Virtual device path")
args = parser.parse_args()

expected_user = args.user.strip().lower()
fps_value = args.fps
device = args.device
VIDEO_DIR = "/home/ubuntu/vid/"
video_path = os.path.join(VIDEO_DIR, args.file)

# Ensure logs directory exists
LOG_DIR = "/home/ubuntu/logs/"
os.makedirs(LOG_DIR, exist_ok=True)

# Create a unique log filename with timestamp
timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join(LOG_DIR, f"{expected_user}_{timestamp_str}_log.txt")

# Get video duration using ffprobe
def get_video_duration(video_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'json', video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        info = json.loads(result.stdout)
        duration = float(info['format']['duration'])
        return duration
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None

# Log validated user
def log_detection(username):
    timestamp = datetime.now().isoformat()
    message = f"[{timestamp}] VALIDATED: User '{username}' detected."
    print(message)
    with open(log_file_path, "a") as f:
        f.write(message + "\n")

# Validate received user
def validate_user(received_name):
    received_name = received_name.strip().lower()
    timestamp = datetime.now().isoformat()
    if received_name == expected_user:
        log_detection(received_name)
    else:
        message = f"[{timestamp}] Rejected: '{received_name}' (expected: '{expected_user}')"
        print(message)
        with open(log_file_path, "a") as f:
            f.write(message + "\n")

# Receive data from server
def receive_data(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                print("Server closed the connection.")
                break
            print(f"\n[Server]: {data}")
            validate_user(data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

# Start socket client
def start_client():
    host = socket.gethostbyname(socket.gethostname())
    port = 42000

    try:
        client_socket = socket.socket()
        client_socket.connect((host, port))
        print(f"Connected to {host}:{port}")

        # Start thread to receive data
        threading.Thread(target=receive_data, args=(client_socket,), daemon=True).start()

        # Continuously send "spit"
        while True:
            client_socket.send(b"spit")
            time.sleep(0.5)

    except Exception as e:
        print(f"Connection error: {e}")

# Start FFmpeg stream
def stream_to_virtual_camera(file_path, device, fps=30):
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ['.mp4', '.mov', '.mkv', '.avi']:
        # Stream video
        command = [
            'sudo', 'ffmpeg',
            '-stream_loop', '-1',
            '-re',
            '-i', file_path,
            '-f', 'v4l2',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-r', str(fps),
            device
        ]
    elif ext in ['.jpg', '.jpeg', '.png']:
        # Loop static image as video
        command = [
            'sudo', 'ffmpeg',
            '-loop', '1',
            '-re',
            '-i', file_path,
            '-f', 'v4l2',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-r', str(fps),
            device
        ]
    else:
        print(f"Unsupported file type: {ext}")
        return

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        
# Main execution
if __name__ == "__main__":
    duration = get_video_duration(video_path)
    if duration:
        print(f"Video duration: {duration:.2f} seconds")

    # Start video streaming in a separate thread
    threading.Thread(target=stream_to_virtual_camera, args=(video_path, device, fps_value), daemon=True).start()

    # Start socket client
    start_client()
