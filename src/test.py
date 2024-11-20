import os
import edge_tts  # Correct import using the library
import playsound

def speak_text(text):
    """Speaks the given text using Edge TTS and plays it directly."""

    tts = edge_tts.EdgeTTS(text=text, voice='en-US-JennyNeural')  # Adjust voice as needed
    audio_file = 'temp.mp3'
    tts.save(audio_file)

    try:
        playsound(audio_file)
    except Exception as e:
        print("Error playing audio:", e)  # Handle playback errors

    os.remove(audio_file)

if __name__ == "__main__":
    text_to_speak = "Hello, world! This is a test using Edge TTS."
    speak_text(text_to_speak)