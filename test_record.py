import sounddevice as sd
import scipy.io.wavfile as wav

# Set parameters
duration = 5  # seconds
sample_rate = 44100  # Hz

print("Recording...")

try:
    # Record audio
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished

    # Save to a WAV file
    wav.write('test_recording.wav', sample_rate, audio_data)
    print("Recording saved as 'test_recording.wav'.")
except Exception as e:
    print(f"An error occurred: {e}")
