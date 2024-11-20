import edge_tts
import playsound
import os

def speak_text(text):
    """Speaks the given text using Edge TTS and plays it directly."""

    tts = edge_tts.EdgeTTS(text=text, voice='en-US-JennyNeural')  # Adjust voice as needed
    audio_file = 'temp.mp3'
    tts.save(audio_file)

    playsound(audio_file)
    os.remove(audio_file)

if __name__ == "__main__":
    text_to_speak = "Hello, world! This is a test using Edge TTS."
    speak_text(text_to_speak)