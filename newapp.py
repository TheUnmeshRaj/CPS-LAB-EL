import time

import cv2
import mediapipe as mp
import numpy as np
import serial
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


arduino = serial.Serial('COM4', 9600)
time.sleep(2)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

current_mode = "gesture"

@app.route('/')
def index():
    return render_template('index.html', mode=current_mode)

@app.route('/switch_mode', methods=['POST'])
def switch_mode():
    global current_mode
    mode = request.get_json().get('mode')
    if mode in ['audio', 'gesture']:
        current_mode = mode
        return jsonify({"status": "success", "mode": current_mode}), 200
    return jsonify({"status": "failure", "message": "Invalid mode"}), 400

@app.route('/update_slider', methods=['POST'])
def update_slider():
    data = request.get_json()
    slider_value = data.get('value')
    print(f"Slider updated: {slider_value}")
    return jsonify({"status": "success"}), 200

def handle_gesture():
    cap = cv2.VideoCapture(0)
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
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                wrist_y = hand_landmarks.landmark[0].y
                index_tip_y = hand_landmarks.landmark[8].y

                angle = index_tip_y - wrist_y

                min_angle = min(min_angle, angle)
                max_angle = max(max_angle, angle)

                if max_angle != min_angle:
                    slider_value = np.interp(angle, [min_angle, max_angle], [0, 100])
                else:
                    slider_value = 0

                slider_value = int(np.clip(slider_value, 0, 100))

                # Map slider value to 360° (full range)
                servo_angle = int((slider_value * 360 / 100))
                print(f"Servo angle: {servo_angle}")

                try:
                    arduino.write(f"{servo_angle}\n".encode())
                except Exception as e:
                    print("Error sending to Arduino:", e)

        cv2.imshow('Hand Tracking', frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/start', methods=['GET'])
def start():
    if current_mode == "gesture":
        handle_gesture()
    return jsonify({"status": "started", "mode": current_mode}), 200

if __name__ == '__main__':
    app.run(debug=True)
