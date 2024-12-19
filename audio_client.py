import re

import requests
import speech_recognition as sr

# Flask API endpoint
FLASK_URL = "http://127.0.0.1:5000/update_slider"

# Function to process recognized commands
def process_command(command,val):
    global slider_value
    if "increase" in command:
        slider_value = min(slider_value + val, 100)  # Increase by 10 (max 100)
    elif "decrease" in command:
        slider_value = max(slider_value - val, 0)  # Decrease by 10 (min 0)
    elif "set" in command:
        # Parse number from command (e.g., "set to 50")
        try:
            number = int([word for word in command.split() if word.isdigit()][0])
            slider_value = max(0, min(100, number))  # Clamp value between 0 and 100
        except (IndexError, ValueError):
            print("Couldn't find a valid number in command.")
            return
    else:
        print("Command not recognized. Try 'increase', 'decrease', or 'set to [value]'.")
        return

    # Send updated slider value to the Flask backend
    try:
        response = requests.post(FLASK_URL, json={"value": slider_value})
        if response.status_code == 200:
            print(f"Slider updated to: {slider_value}")
        else:
            print("Failed to update slider on server.")
    except requests.exceptions.RequestException as e:
        print("Error sending slider value:", e)

# Initialize the slider value
slider_value = 50  # Default starting point

# Main function for audio commands
def listen_for_commands():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Listening for commands... (say 'increase', 'decrease', or 'set to [value]')")

    while True:
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
                print("Say something...")
                audio = recognizer.listen(source)

            # Recognize speech using Google Web Speech API
            command = recognizer.recognize_google(audio).lower()
            val = int(re.search(r'\d+', command).group()) if re.search(r'\d+', command) else None

            print(f"Recognized command: {command}")

            # Process the command
            process_command(command,val)

        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Please try again.")
        except sr.RequestError as e:
            print(f"Speech Recognition API error: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    listen_for_commands()
