import speech_recognition as sr
from gtts import gTTS
import os

def recognize_speech_from_mic(device_index=3):
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index=device_index) as source:
        print("Please say something:")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print("You said: " + text)
        return text
    except sr.UnknownValueError:
        print("Google Web Speech API could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")
        return None

def speak(text, lang='en'):
    """ Generate speech from text using gTTS and play using mpv """
    tts = gTTS(text=text, lang=lang)
    output_file = "temp.mp3"
    tts.save(output_file)
    command = f'mpv --no-terminal {output_file}'
    os.system(command)
    os.remove(output_file)