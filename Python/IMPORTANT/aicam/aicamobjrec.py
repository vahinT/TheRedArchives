import cv2
import sys
from ultralytics import YOLO

# Load YOLOv8 nano model (fast + accurate)
model = YOLO("yolov8n.pt")

# Open default camera (0)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Force camera resolution (prevents auto zoom on some webcams)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("❌ Cannot access camera")
    sys.exit(1)

print("✅ Camera started. Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Frame capture failed")
        break

    # YOLO inference directly on raw frame (NO resizing by us)
    results = model(frame, conf=0.4, iou=0.5, verbose=False)[0]

    # Draw detections
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = model.names[cls]

        text = f"{label} {conf:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame,
            text,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

    cv2.imshow("AI Camera (No Zoom)", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
