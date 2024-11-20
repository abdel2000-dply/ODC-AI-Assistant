import speech_recognition as sr
import pyttsx3 as tts

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
    """ Generate speech from text using pyttsx3 """
    engine = tts.init()
    voices = engine.getProperty('voices')
    
    # Iterate through available voices and set the desired one
    for voice in voices:
        print(f"Using voice: {voice.name}")
        engine.setProperty('voice', voice.id)
        engine.setProperty('rate', 150)  # Speed percent (can go over 100)
        engine.setProperty('volume', 1)  # Volume 0-1
        engine.say(text)
        engine.runAndWait()