import speech_recognition as sr
import os
import edge_tts
import asyncio
from langdetect import detect

def recognize_speech_from_mic(device_index=None):  # Changed to None to auto-detect
    recognizer = sr.Recognizer()
    try:
        # List available microphones
        mics = sr.Microphone.list_microphone_names()
        print(f"Available microphones: {mics}")
        
        # Try to find USB audio device
        if device_index is None:
            for index, name in enumerate(mics):
                if 'USB' in name.upper():  # Case insensitive search
                    device_index = index
                    print(f"Found USB microphone at index {index}: {name}")
                    break
        
        if device_index is None:
            device_index = 2  # Try the bcm2835 device as fallback
        
        print(f"Using microphone device index: {device_index}")
        
        with sr.Microphone(device_index=device_index, sample_rate=44100) as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening...")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Audio captured successfully")
            except Exception as e:
                print(f"Error capturing audio: {e}")
                return None

        try:
            text = recognizer.recognize_google(audio)
            print("You said: " + text)

            # Detect the language of the recognized text
            detected_lang = detect(text)
            print(f"Detected language: {detected_lang}")

            # Map detected language to Google Speech API language codes
            lang_map = {
                'en': 'en-US',
                'fr': 'fr-FR',
                'ar': 'ar-MA'  # Arabic (Morocco)
            }
            language = lang_map.get(detected_lang, 'en-US')

            # Recognize speech again with the detected language
            text = recognizer.recognize_google(audio, language=language)
            print(f"You said (in {language}): " + text)
            return text
            
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
            
    except Exception as e:
        print(f"Error with microphone: {e}")
        print(f"Current device_index: {device_index}")
        return None

async def speak(text, lang='en'):
    """ Generate speech from text using edge-tts and play using mpv """
    voice = 'en-US-AndrewMultilingualNeural'
    output_file = "temp.mp3"

    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        
        # Use playsound instead of mpv for better compatibility
        from playsound import playsound
        playsound(output_file)
    except Exception as e:
        print(f"Error during TTS or playback: {e}")  # Informative error message
    finally:
        # Ensure temporary file is removed even if exceptions occur
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except:
                pass