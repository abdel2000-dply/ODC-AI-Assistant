import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from webrtc_audio_processing import AudioProcessingModule

# Set parameters
duration = 5  # seconds
sample_rate = 44100  # Hz

print("Recording...")

try:
    # Record audio
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished

    # Apply noise reduction using webrtc-audio-processing
    apm = AudioProcessingModule()
    reduced_noise_audio = apm.process_stream(audio_data.flatten(), sample_rate)

    # Save to a WAV file
    wav.write('test_recording_filtered.wav', sample_rate, reduced_noise_audio.astype(np.int16))
    print("Recording saved as 'test_recording_filtered.wav'.")
except Exception as e:
    print(f"An error occurred: {e}")
