import pyttsx3

engine = pyttsx3.init()

# Set properties (optional)
engine.setProperty('rate', 150)  # Adjust speech rate
engine.setProperty('volume', 1.0)  # Adjust volume

# Text to be spoken
text = "Hello, world! This is a text-to-speech example."

# Speak the text
engine.say(text)
engine.runAndWait()