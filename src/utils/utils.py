import speech_recognition as sr
import os
import wave
import pyaudio
from groq import Groq
import edge_tts
import asyncio
from langdetect import detect
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY') 

def recognize_speech_from_mic(device_index=0):
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index=device_index) as source:
        print("Please say something:")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

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

        text = recognizer.recognize_google(audio, language=language)
        print(f"You said (in {language}): " + text)
        return text

    except Exception as e:
        print(f"Error recognizing speech: {e}")
        return None

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