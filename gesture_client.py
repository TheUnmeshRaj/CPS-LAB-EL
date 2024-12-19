import cv2
import mediapipe as mp
import numpy as np
import requests

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_drawing = mp.solutions.drawing_utils

FLASK_URL = "http://127.0.0.1:5000/update_slider"

def calculate_angle(y_tip, y_wrist):
    """Return angle of hand based on fingertips (vertical vs horizontal)."""
    return y_tip - y_wrist

cap = cv2.VideoCapture(0)

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

            # Map the angle to a slider value (0 to 100)
            slider_value = np.interp(angle, [-0.5, 0.5], [0, 100])
            slider_value = int(np.clip(slider_value, 0, 100))

            print("Slider Value:", slider_value)

            try:
                requests.post(FLASK_URL, json={"value": slider_value})
            except requests.exceptions.RequestException as e:
                print("Error:", e)

    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
