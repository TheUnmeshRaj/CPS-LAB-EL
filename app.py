from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

slider_value = 0  

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

if __name__ == '__main__':
    app.run(debug=True)
