import speech_recognition as sr
import os
import wave
import pyaudio
from groq import Groq
import edge_tts
import asyncio
from dotenv import load_dotenv
import noisereduce as nr
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY') 

def recognize_speech_from_mic(language='en-US', device_index=3):
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone(device_index=device_index) as source:  # Use specific device index
            print("Please say something:")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5)
    except OSError as e:
        print(f"Could not access the microphone (device index {device_index}): {e}")
        return None
    except AttributeError as e:
        print(f"Microphone stream error: {e}")
        return None

    try:
        # Recognize speech using Google's speech recognition
        text = recognizer.recognize_google(audio)
        print("You said: " + text)

        # Recognize speech again with the detected language
        text = recognizer.recognize_google(audio, language=language)
        print(f"You said (in {language}): " + text)
        return text

    except sr.RequestError:
        # API was unreachable or unresponsive
        print("API unavailable")
        return None
    except sr.UnknownValueError:
        # Speech was unintelligible
        print("Unable to recognize speech")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def speak(text, lang='en'):
    """ Generate speech from text using edge-tts and play using mpv """
    voice = 'en-US-EmmaMultilingualNeural'  # Adjust voice as needed
    output_file = "temp.mp3"

    try:
        # Generate speech using edge-tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

        # Play the audio file using mpv
        command = f'mpv --no-terminal {output_file}'
        # command = fr'"C:\Users\Home\Downloads\mpv-i686-w64-mingw32\mpv.exe" {output_file}'
        os.system(command)
    except Exception as e:
        print(f"Error during TTS or playback: {e}")  # Informative error message
    finally:
        # Ensure temporary file is removed even if exceptions occur
        if os.path.exists(output_file):
            os.remove(output_file)


def record_audio_to_file(file_name="live_audio.wav", duration=5, sample_rate=44100):
    """Records audio from the microphone, applies noise reduction, and saves it to a WAV file."""
    print("Recording...")

    try:
        # Record audio
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()  # Wait until recording is finished

        # Apply noise reduction
        audio_data = audio_data.flatten()
        reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)

        # Save to a WAV file
        wav.write(file_name, sample_rate, reduced_noise_audio.astype(np.int16))
        print(f"Recording saved as '{file_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

def record_audio_to_file_stream(frames, file_name="live_audio.wav", sample_rate=44100):
    """Saves a list of audio frames to a WAV file with noise reduction."""
    try:
        # Convert frames to numpy array
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)

        # Apply noise reduction
        reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)

        # Save the audio to file
        wav.write(file_name, sample_rate, reduced_noise_audio.astype(np.int16))
        print(f"Recording saved as '{file_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

def transcribe_audio_with_groq(audio_file="live_audio.wav", language="en"):
    """Transcribes audio using Groq API."""
    client = Groq(api_key=groq_api_key)
    with open(audio_file, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_file, file.read()),
            model="whisper-large-v3",  # Specify the model
            language=language,  # Specify the language
            response_format="text"          # Use "text" for a simple string response
        )
    return transcription  # Returns the plain transcription text

def play_audio_file(file_name):
    """Plays the specified WAV audio file."""
    chunk = 1024
    wf = wave.open(file_name, 'rb')
    p = pyaudio.PyAudio()

    # Open a stream for playback
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data in chunks and play
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    file_name = "test_audio.wav"
    record_audio_to_file(file_name)
    print(f"Audio recorded and saved to {file_name}.")
    print("now playing the audio file")
    play_audio_file(file_name)