from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

slider_value = 0  # Default slider value
current_mode = "audio"  # Default mode: "audio" or "visual"

def map_slider_to_servo(slider_val):
    """Maps the slider value (0-100) to servo angle (-90 to +90)."""
    return (slider_val * 180 / 100) - 90  # Map to range -90 to 90

@app.route('/')
def index():
    return render_template('index.html', slider=slider_value)

@app.route('/get_slider', methods=['GET'])
def get_slider():
    """Returns the current slider value."""
    return jsonify({"slider": slider_value})

@app.route('/update_slider', methods=['POST'])
def update_slider():
    """Updates the slider value and prints the mapped servo angle."""
    global slider_value
    data = request.get_json()
    slider_value = data.get("value", 0)
    print(f"Slider updated to: {slider_value}")

    # Map slider value to servo angle
    angle = map_slider_to_servo(slider_value)
    print(f"Mapped angle: {angle}")

    return jsonify({"status": "success", "slider_value": slider_value})

@app.route('/set_mode', methods=['POST'])
def set_mode():
    """Sets the current mode to 'audio' or 'visual'."""
    global current_mode
    data = request.get_json()
    current_mode = data.get("mode", "audio")
    print(f"Mode switched to: {current_mode}")
    return jsonify({"status": "success", "mode": current_mode})

@app.route('/get_mode', methods=['GET'])
def get_mode():
    """Returns the current mode."""
    return jsonify({"mode": current_mode})

if __name__ == '__main__':
    app.run(debug=True)
