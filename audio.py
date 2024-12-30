import re
import time

import requests
import serial
import speech_recognition as sr

# Flask URL for slider updates
FLASK_URL = "http://127.0.0.1:5000/update_slider"

# Arduino Serial Port
arduino = serial.Serial('COM4', 9600)  # Replace 'COM3' with your Arduino's port
time.sleep(2)  # Wait for serial connection to initialize

slider_value = 50  # Initial slider value


def map_slider_to_servo(slider_val):
    """Maps the slider value (0-100) to servo angle (-90 to +90)."""
    return int((slider_val * 180 / 100) - 90)  # Map to range -90 to +90


def process_command(command, val):
    """Process voice command and update slider value."""
    global slider_value
    if "increase" in command:
        slider_value = min(slider_value + (val or 10), 100)  # Default increment is 10
    elif "decrease" in command:
        slider_value = max(slider_value - (val or 10), 0)  # Default decrement is 10
    elif "set" in command:
        try:
            number = int([word for word in command.split() if word.isdigit()][0])
            slider_value = max(0, min(100, number))
        except (IndexError, ValueError):
            print("Couldn't find a valid number in the command.")
            return
    else:
        print("Command not recognized. Try 'increase', 'decrease', or 'set to [value]'.")
        return

    # Send slider value to Flask server
    try:
        response = requests.post(FLASK_URL, json={"value": slider_value})
        if response.status_code == 200:
            print(f"Slider updated to: {slider_value}")
        else:
            print("Failed to update slider on the server.")
    except requests.exceptions.RequestException as e:
        print("Error sending slider value to server:", e)

    # Map slider value to servo angle and send to Arduino
    servo_angle = map_slider_to_servo(slider_value)
    try:
        arduino.write(f"{servo_angle}\n".encode())
        print(f"Servo angle sent: {servo_angle}")
    except Exception as e:
        print("Error sending servo angle to Arduino:", e)


def listen_for_commands():
    """Listen for voice commands and process them."""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Listening for commands... (say 'increase', 'decrease', or 'set to [value]')")

    while True:
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
                print("Say something...")
                audio = recognizer.listen(source)

            # Convert speech to text
            command = recognizer.recognize_google(audio).lower()
            val = int(re.search(r'\d+', command).group()) if re.search(r'\d+', command) else None

            print(f"Recognized command: {command}")

            # Process the command
            process_command(command, val)

        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Please try again.")
        except sr.RequestError as e:
            print(f"Speech Recognition API error: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    listen_for_commands()
    arduino.close()
