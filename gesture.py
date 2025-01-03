import time

import cv2
import mediapipe as mp
import numpy as np
import requests
import serial

# Flask server URL
FLASK_URL = "http://127.0.0.1:5000/update_slider"

# Arduino Serial Port
arduino = serial.Serial('COM4', 9600)  # Replace 'COM3' with your Arduino's port
time.sleep(2)  # Wait for the serial connection to initialize

# Mediapipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(y_tip, y_wrist):
    """Return angle of hand based on fingertips (vertical vs horizontal)."""
    return y_tip - y_wrist

cap = cv2.VideoCapture(0)

# Tracking the min/max values to map to 0-100
min_angle = float('inf')
max_angle = float('-inf')

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
            )

            wrist_y = hand_landmarks.landmark[0].y
            index_tip_y = hand_landmarks.landmark[8].y

            angle = calculate_angle(index_tip_y, wrist_y)

            # Track min/max angle
            min_angle = min(min_angle, angle)
            max_angle = max(max_angle, angle)

            # Map the angle to a slider value (0 to 100)
            if max_angle != min_angle:
                slider_value = np.interp(angle, [min_angle, max_angle], [0, 100])
            else:
                slider_value = 0  # If the min and max are equal, set it to 0 (or some default)

            slider_value = int(np.clip(slider_value, 0, 100))

            # Map slider value to servo angle (-90 to +90)
            servo_angle = int((slider_value * 180 / 100) - 90)

            print(f"Slider Value: {slider_value}, Servo Angle: {servo_angle}")

            # Send slider value to Flask server
            try:
                requests.post(FLASK_URL, json={"value": slider_value})
            except requests.exceptions.RequestException as e:
                print("Error sending to Flask:", e)

            # Send servo angle to Arduino via Serial
            try:
                arduino.write(f"{servo_angle}\n".encode())
            except Exception as e:
                print("Error sending to Arduino:", e)

    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
