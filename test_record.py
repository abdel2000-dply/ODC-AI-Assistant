import pyaudio
import wave
from src.utils.utils import recognize_speech_from_mic

def record_audio(file_name="test_audio.wav", record_seconds=5, device_index=3):
    """Records audio from the specified microphone and saves it to a WAV file."""
    p = pyaudio.PyAudio()

    # Open a stream for recording
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=1024)

    print("Recording... Speak into the microphone.")
    frames = []

    try:
        for _ in range(0, int(16000 / 1024 * record_seconds)):
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

def main():
    print("Starting audio recording test...")
    record_audio()
    print("Audio recording saved as 'test_audio.wav'.")

if __name__ == "__main__":
    main()
