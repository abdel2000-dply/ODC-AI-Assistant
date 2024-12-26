import pyaudio
import wave
from src.utils.utils import recognize_speech_from_mic

def get_valid_sample_rate(device_index):
    """Get a valid sample rate for the specified device."""
    p = pyaudio.PyAudio()
    info = p.get_device_info_by_index(device_index)
    supported_rates = [8000, 16000, 32000, 44100, 48000]
    for rate in supported_rates:
        if p.is_format_supported(rate,
                                 input_device=info["index"],
                                 input_channels=info["maxInputChannels"],
                                 input_format=pyaudio.paInt16):
            return rate
    return None

def record_audio(file_name="test_audio.wav", record_seconds=5, device_index=3):
    """Records audio from the specified microphone and saves it to a WAV file."""
    p = pyaudio.PyAudio()

    # Get a valid sample rate for the device
    sample_rate = get_valid_sample_rate(device_index)
    if sample_rate is None:
        print(f"No valid sample rate found for device index {device_index}")
        return

    # Open a stream for recording
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=1024)

    print(f"Recording at {sample_rate} Hz... Speak into the microphone.")
    frames = []

    try:
        for _ in range(0, int(sample_rate / 1024 * record_seconds)):
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
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

def main():
    print("Starting audio recording test...")
    record_audio()
    print("Audio recording saved as 'test_audio.wav'.")

if __name__ == "__main__":
    main()
