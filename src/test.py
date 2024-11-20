import os
import edge_tts  # Correct import using the library
import playsound

def speak_text(text):
    """Speaks the given text using Edge TTS and plays it directly.

    Handles potential errors during TTS conversion or audio playback.
    """

    try:
        # Potential name change (check examples for actual name)
        tts = edge_tts.TextToSpeech(text=text, voice='en-US-JennyNeural')  # Adjust voice as needed
        audio_file = 'temp.mp3'
        tts.save(audio_file)

        playsound(audio_file)
    except Exception as e:
        print(f"Error during TTS or playback: {e}")  # Informative error message
    finally:
        # Ensure temporary file is removed even if exceptions occur
        if os.path.exists(audio_file):
            os.remove(audio_file)

if __name__ == "__main__":
    text_to_speak = "Hello, world! This is a test using Edge TTS."
    speak_text(text_to_speak)