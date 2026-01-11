import subprocess
import sys
import importlib.util
import threading
import time
import os

# Required packages
required_packages = [
    "opencv-python",
    "torch",
    "ultralytics",
    "numpy"
]

# Spinner animation
class Spinner:
    def __init__(self, message="Installing required packages"):
        self.message = message
        self.running = False
        self.thread = None

    def spinner_task(self):
        spinner_chars = ['|', '/', '-', '\\']
        idx = 0
        while self.running:
            print(f"\r{self.message}... {spinner_chars[idx % len(spinner_chars)]}", end='', flush=True)
            idx += 1
            time.sleep(0.2)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.spinner_task)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
        print("\rInstallation complete!            ")

# Check for missing packages
def install_missing_packages(packages):
    missing = []
    for package in packages:
        name = package.split('-')[0]
        if importlib.util.find_spec(name) is None:
            missing.append(package)
    return missing

# Install packages with spinner
missing = install_missing_packages(required_packages)
if missing:
    spinner = Spinner()
    spinner.start()
    for package in missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    spinner.stop()

# --- Real-time Object Detection ---
import cv2
import torch
from ultralytics import YOLO
import numpy as np

# Load YOLOv8 model (n = nano)
model = YOLO("yolov8n.pt")  # Make sure this is downloaded automatically

# Start front camera (0 or 1 based on your system)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Cannot access camera.")
    sys.exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Convert to RGB for YOLO
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect objects
    results = model(rgb)[0]

    # Draw all bounding boxes
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = model.names[cls]
        text = f"{label} {conf:.2f}"

        # Draw hollow rectangle and label
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, text, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Display the frame
    cv2.imshow("Object Detection", frame)

    # Quit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
