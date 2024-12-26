import os
from groq import Groq
import pyaudio
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')

# Initialize the Groq client
client = Groq(api_key=groq_api_key)

def record_audio_to_file(file_name):
    import speech_recognition as sr

    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"Device Index {index}: {name}")



    import wave
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

# Record and process audio
audio_file = "live_audio.wav"
record_audio_to_file(audio_file)

# Transcribe the recorded audio
with open(audio_file, "rb") as file:
    transcription = client.audio.transcriptions.create(
        file=(audio_file, file.read()),
        model="whisper-large-v3-turbo",  # Choose a model
        response_format="text"          # Set to "text" for a simple response
    )
    print(transcription)
