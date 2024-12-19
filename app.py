from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

slider_value = 0  # Current slider value

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
    return jsonify({"status": "success", "slider_value": slider_value})

@app.route('/audio_command', methods=['POST'])
def audio_command():
    global slider_value
    data = request.get_json()
    command = data.get("command", "").lower()

    try:
        # Extract value from audio command
        new_value = int(command.split()[-1])
        if 0 <= new_value <= 100:
            slider_value = new_value
            print(f"Audio command updated slider to: {slider_value}")
            return jsonify({"status": "success", "slider_value": slider_value})
        else:
            return jsonify({"status": "error", "message": "Value out of range"}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid command format"}), 400

if __name__ == '__main__':
    app.run(debug=True)
