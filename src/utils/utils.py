import speech_recognition as sr
import os
import wave
import pyaudio
from groq import Groq
import edge_tts
import asyncio
from langdetect import detect
from dotenv import load_dotenv
import time

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY') 

def recognize_speech_from_mic():
    """
    Recognizes speech using the default microphone and Google Speech Recognition,
    with user-selected device and language detection.
    Returns:
        str: The recognized text, or None if an error occurred.
    """

    try:
        # Create a PyAudio instance
        p = pyaudio.PyAudio()

        # List available input devices
        print("Available Input Devices:")
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        input_devices = []
        for i in range(numdevices):
            if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                device_name = p.get_device_info_by_host_api_device_index(0, i).get('name')
                print(f"  ID {i}: {device_name}")
                input_devices.append(i)

        if not input_devices:
            print("No input devices found. Please ensure a microphone is connected.")
            return None

        # User Select Device
        while True:
            try:
                device_index = int(input("Enter the ID of the microphone you want to use: "))
                if device_index in input_devices:
                     break
                else:
                     print("Invalid device ID. Please choose from the list above.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        # Create a speech recognition object
        recognizer = sr.Recognizer()

        # Use PyAudio to create an audio source
        with sr.Microphone(device_index=device_index) as source:
            print("Please wait, adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Ready, please speak into the microphone...")
            start_time = time.time()
            audio = recognizer.listen(source, timeout=10)
            end_time = time.time()
            print(f"Speech captured in {end_time-start_time:.2f} seconds")

        # Recognize speech using Google's speech recognition
        text = recognizer.recognize_google(audio)
        print("Initial recognition: " + text)

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

    except sr.RequestError as e:
        print(f"Google Speech Recognition API unavailable. Request Error: {e}")
        return None
    except sr.UnknownValueError as e:
        print(f"Google Speech Recognition could not understand audio. Unknown value error: {e}")
        return None
    except ValueError as e:
      print(f"Value Error: {e}. Check if the audio index you provided is valid.")
      return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    finally:
        if 'p' in locals() and isinstance(p, pyaudio.PyAudio):
            p.terminate()

async def speak(text, lang='en'):
    """ Generate speech from text using edge-tts and play using mpv """
    voice = 'en-US-AndrewMultilingualNeural'  # Adjust voice as needed
    output_file = "temp.mp3"

    try:
        # Generate speech using edge-tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

        # Play the audio file using mpv
        command = f'mpv --no-terminal {output_file}'
        os.system(command)
    except Exception as e:
        print(f"Error during TTS or playback: {e}")  # Informative error message
    finally:
        # Ensure temporary file is removed even if exceptions occur
        if os.path.exists(output_file):
            os.remove(output_file)

# Initialize the Groq client
client = Groq(api_key=groq_api_key)

def record_audio_to_file(file_name="live_audio.wav"):
    """Records audio from the microphone and saves it to a WAV file."""
    p = pyaudio.PyAudio()

    # Open a stream for recording
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024)

    print("Recording... Speak into the microphone.")
    frames = []

    try:
        for _ in range(0, int(16000 / 1024 * 5)):  # Record for 5 seconds
            data = stream.read(1024)
            frames.append(data)
    except KeyboardInterrupt:
        pass

    print("Recording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the audio to file
    wf = wave.open(file_name, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio_with_groq(audio_file="live_audio.wav"):
    """Transcribes audio using Groq API."""
    with open(audio_file, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_file, file.read()),
            model="whisper-large-v3-turbo",  # Specify the model
            response_format="text"          # Use "text" for a simple string response
        )
    return transcription  # Returns the plain transcription text