from flask import Flask, jsonify, render_template, request
from gpiozero import AngularServo
import time

app = Flask(__name__)

slider_value = 0  
SERVO_PIN = 17
servo = AngularServo(SERVO_PIN, min_angle=-90, max_angle=90)

def map_slider_to_servo(slider_val):
    """Maps the slider value (0-100) to servo angle (-90 to +90)."""
    return (slider_val * 180 / 100) - 90  # Map to range -90 to 90

@app.route('/')
def index():
    return render_template('index.html', slider=slider_value)

@app.route('/get_slider', methods=['GET'])
def get_slider():
    return jsonify({"slider": slider_value})

@app.route('/update_slider', methods=['POST'])
def update_slider():
    global slider_value
    data = request.get_json()
    slider_value = data.get("value", 0)
    print(f"Slider updated to: {slider_value}")

    # Map the slider value to servo angle
    angle = map_slider_to_servo(slider_value)
    servo.angle = angle  # Update servo position

    return jsonify({"status": "success", "slider_value": slider_value})

@app.route('/audio_command', methods=['POST'])
def audio_command():
    global slider_value
    data = request.get_json()
    command = data.get("command", "").lower()

    try:
        new_value = int(command.split()[-1])
        if 0 <= new_value <= 100:
            slider_value = new_value
            print(f"Audio command updated slider to: {slider_value}")
            
            # Map the slider value to servo angle
            angle = map_slider_to_servo(slider_value)
            servo.angle = angle  # Update servo position
            
            return jsonify({"status": "success", "slider_value": slider_value})
        else:
            return jsonify({"status": "error", "message": "Value out of range"}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid command format"}), 400

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        pass
    finally:
        servo.detach()  # Detach servo when the app is stopped
