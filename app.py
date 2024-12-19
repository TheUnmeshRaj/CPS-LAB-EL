from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

slider_value = 0  # Default slider value

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

    # Normally here you would control the servo with the ESP8266, but for now, we update slider value
    angle = map_slider_to_servo(slider_value)
    print(f"Mapped angle: {angle}")  # Just print out the angle

    return jsonify({"status": "success", "slider_value": slider_value})

if __name__ == '__main__':
    app.run(debug=True)
