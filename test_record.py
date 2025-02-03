import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from scipy.signal import butter, lfilter

# Set parameters
duration = 5  # seconds
sample_rate = 44100  # Hz

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

print("Recording...")

try:
    # Record audio
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished

    # Apply bandpass filter to remove noise
    lowcut = 300.0  # Low cut frequency in Hz
    highcut = 3400.0  # High cut frequency in Hz
    filtered_audio = bandpass_filter(audio_data.flatten(), lowcut, highcut, sample_rate)

    # Save to a WAV file
    wav.write('test_recording_filtered.wav', sample_rate, filtered_audio.astype(np.int16))
    print("Recording saved as 'test_recording_filtered.wav'.")
except Exception as e:
    print(f"An error occurred: {e}")
