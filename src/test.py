import gtts
from playsound import playsound
import os

def speak_text(text):
    """Speaks the given text using Google Text-to-Speech and plays it directly."""
    tts = gtts.gTTS(text=text, lang='en')  # Adjust language as needed
    tts.save('temp.mp3')  # Temporarily save to memory

    playsound('temp.mp3')  # Play the audio
    os.remove('temp.mp3')  # Delete the temporary file

# Example usage
if __name__ == "__main__":
    text_to_speak = "Hello, world! This is a test using Google Text-to-Speech."
    speak_text(text_to_speak)