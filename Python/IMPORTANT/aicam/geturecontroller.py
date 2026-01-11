import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import sys
import os

# ================== CONFIG ==================
BSOD_IMAGE_PATH = r"C:\Users\vahinm\Desktop\pic\images.jfif"  # <-- PUT YOUR IMAGE PATH HERE
WINDOW_NAME = "Gesture Controller (Mini)"
CAM_WIDTH = 420
CAM_HEIGHT = 300
COOLDOWN = 1.2  # seconds between key presses
# ============================================

last_action_time = 0

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

if not cap.isOpened():
    print("❌ Camera not accessible")
    sys.exit(1)

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, CAM_WIDTH, CAM_HEIGHT)

def count_fingers(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    fingers = 0

    # Thumb
    if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[tips[0] - 1].x:
        fingers += 1

    # Other fingers
    for tip in tips[1:]:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers += 1

    return fingers


print("✅ Gesture controller started")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers = count_fingers(hand_landmarks)

            current_time = time.time()
            if current_time - last_action_time > COOLDOWN:
                if fingers == 1:
                    pyautogui.press("space")
                    print("🖐️ 1 finger → SPACE")
                    last_action_time = current_time

                elif fingers == 2:
                    pyautogui.press("l")
                    print("✌️ 2 fingers → L")
                    last_action_time = current_time

                elif fingers == 3:
                    pyautogui.press("j")
                    print("🤟 3 fingers → J")
                    last_action_time = current_time


            cv2.putText(
                frame,
                f"Fingers: {fingers}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    cv2.imshow(WINDOW_NAME, frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
