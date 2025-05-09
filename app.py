import cv2
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import requests
import json
from datetime import datetime

# Load allowed users
def load_users(file_path="users.json"):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            return set(data.get("users", []))
    except Exception as e:
        print(f"[ERROR] Failed to load users: {e}")
        return set()

# Validate detected person name
def validate_user(name, valid_users):
    if name in valid_users:
        result = "GRANTED"
        print("Passed")
    else:
        result = "DENIED"
        print("Failed")
    log_access(name, result)

# Log access result
def log_access(name, result):
    with open("access_log.txt", "a") as f:
        f.write(f"{datetime.now()} - {name} - {result}\n")

# Request person name from face detection service
def fetch_person_name():
    try:
        response = requests.get("http://localhost:5000/person_name", timeout=2)
        return response.json().get("name", "Unknown")
    except Exception as e:
        print("[ERROR] Face detection request failed:", e)
        return "Unknown"

# Calculate brightness
def calculate_brightness(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return np.mean(gray)

# Calculate contrast
def calculate_contrast(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return np.std(gray)

# Setup matplotlib plots
def setup_plot():
    plt.ion()
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))

    ax[0].set_title('Real-time Brightness')
    ax[0].set_ylim(0, 255)
    brightness_line, = ax[0].plot([], [], 'b')

    ax[1].set_title('Real-time Contrast')
    ax[1].set_ylim(0, 100)
    contrast_line, = ax[1].plot([], [], 'r')

    return fig, ax, brightness_line, contrast_line

# Update live graph
def update_plot(brightness_vals, contrast_vals, brightness_line, contrast_line, ax):
    x = list(range(len(brightness_vals)))
    brightness_line.set_xdata(x)
    brightness_line.set_ydata(brightness_vals)

    contrast_line.set_xdata(x)
    contrast_line.set_ydata(contrast_vals)

    for a in ax:
        a.relim()
        a.autoscale_view()

    plt.pause(0.01)

# Main video analysis function
def analyze_video(video_source=0):
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print("[ERROR] Cannot open video source.")
        return

    valid_users = load_users()
    fig, ax, brightness_line, contrast_line = setup_plot()
    brightness_vals = deque(maxlen=100)
    contrast_vals = deque(maxlen=100)

    frame_interval = 30  # Check face every 30 frames
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        brightness_vals.append(calculate_brightness(frame))
        contrast_vals.append(calculate_contrast(frame))
        update_plot(brightness_vals, contrast_vals, brightness_line, contrast_line, ax)

        frame_count += 1
        if frame_count % frame_interval == 0:
            name = fetch_person_name()
            print(f"[INFO] Detected: {name}")
            validate_user(name, valid_users)

        cv2.imshow("Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    plt.ioff()
    plt.show()

# Start analysis
if __name__ == "__main__":
    analyze_video(0)  # 0 = default webcam
