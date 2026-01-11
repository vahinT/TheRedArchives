import subprocess
import sys
import importlib.util
import threading
import time
import tkinter as tk
from tkinter import ttk

# --- Install required packages with GUI loading ---
required_packages = [
    "opencv-python",
    "torch",
    "ultralytics",
    "numpy"
]

def find_missing_packages():
    missing = []
    for pkg in required_packages:
        if importlib.util.find_spec(pkg.split('-')[0]) is None:
            missing.append(pkg)
    return missing

class Loader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Installing")
        self.root.geometry("300x90")
        self.label = ttk.Label(self.root, text="Installing dependencies...")
        self.label.pack(expand=True, padx=10, pady=20)
        self.running = True

    def start(self):
        threading.Thread(target=self.animate).start()
        self.root.mainloop()

    def animate(self):
        dots = ""
        while self.running:
            dots = dots + "." if len(dots) < 3 else ""
            self.label.config(text=f"Installing dependencies{dots}")
            time.sleep(0.4)

    def stop(self):
        self.running = False
        self.root.quit()
        self.root.destroy()

missing = find_missing_packages()
if missing:
    loader = Loader()
    threading.Thread(target=loader.start).start()
    for pkg in missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
    loader.stop()

# ---------------- Object Detection (Optimized) ----------------
import cv2
import torch
from ultralytics import YOLO
import numpy as np

# Load lightweight YOLOv8n
model = YOLO("yolov8n.pt")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Use lower res cam frame to save RAM/CPU
FRAME_WIDTH = 640
FRAME_HEIGHT = 360

# Use every Nth frame only
FRAME_SKIP = 2
frame_count = 0

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

if not cap.isOpened():
    print("Camera not available.")
    sys.exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    if frame_count % FRAME_SKIP == 0:
        # Detect objects (no RGB conversion needed with YOLOv8)
        results = model(frame, verbose=False)[0]

        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            text = f"{label} {conf:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, text, (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Fast YOLOv8 Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
