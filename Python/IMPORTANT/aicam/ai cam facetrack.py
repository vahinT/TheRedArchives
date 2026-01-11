import subprocess
import sys
import importlib.util
import threading
import time
import tkinter as tk
from tkinter import ttk

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

# ---------------- Object Detection + Person Zoom ----------------
import cv2
import torch
from ultralytics import YOLO
import numpy as np

model = YOLO("yolov8n.pt")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera not available.")
    sys.exit()

# Maximize OpenCV window
cv2.namedWindow("Face Tracker", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Face Tracker", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

ZOOM_FACTOR = 1.5

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)[0]
    closest_person_box = None
    max_area = 0

    for box in results.boxes:
        cls_id = int(box.cls[0])
        if model.names[cls_id] != "person":
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        area = (x2 - x1) * (y2 - y1)
        if area > max_area:
            max_area = area
            closest_person_box = (x1, y1, x2, y2)

    if closest_person_box:
        x1, y1, x2, y2 = closest_person_box
        # Center and zoom
        person_crop = frame[y1:y2, x1:x2]

        if person_crop.size != 0:
            person_h, person_w = person_crop.shape[:2]
            zoomed = cv2.resize(person_crop, None, fx=ZOOM_FACTOR, fy=ZOOM_FACTOR, interpolation=cv2.INTER_LINEAR)

            # Optional: Draw label
            cv2.putText(zoomed, "Closest Person", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

            cv2.imshow("Face Tracker", zoomed)
        else:
            cv2.imshow("Face Tracker", frame)
    else:
        cv2.imshow("Face Tracker", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
