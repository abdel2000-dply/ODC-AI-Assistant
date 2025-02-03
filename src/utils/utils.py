import speech_recognition as sr
import os
import wave
import pyaudio
from groq import Groq
import edge_tts
import asyncio
from dotenv import load_dotenv

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
        for _ in range(0, int(16000 / 1024 * 8)):  # Record for 5 seconds
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

def record_audio_to_file_stream(frames, file_name="live_audio.wav", pyaudio_instance = None):
    """Saves a list of audio frames to a WAV file."""
    if pyaudio_instance is None:
        pyaudio_instance = pyaudio.PyAudio()
    wf = wave.open(file_name, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio_instance.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

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