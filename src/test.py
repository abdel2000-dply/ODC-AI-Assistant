import os
import edge_tts
import pyaudio
import wave
from pydub import AudioSegment

async def speak_text(text):
    """Speaks the given text using Edge TTS and plays it directly."""
    voice = 'en-US-AndrewMultilingualNeural'  # Adjust voice as needed
    mp3_file = 'temp.mp3'
    wav_file = 'temp.wav'

    try:
        # Generate speech using edge-tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(mp3_file)

        # Convert MP3 to WAV
        audio = AudioSegment.from_mp3(mp3_file)
        audio.export(wav_file, format="wav")

        # Play the audio file using pyaudio
        wf = wave.open(wav_file, 'rb')
        p = pyaudio.PyAudio()

        # Open a stream
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # Read data in chunks
        chunk = 1024
        data = wf.readframes(chunk)

        # Play the audio file
        while data:
            stream.write(data)
            data = wf.readframes(chunk)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()

        # Close PyAudio
        p.terminate()

    except Exception as e:
        print(f"Error during TTS or playback: {e}")  # Informative error message
    finally:
        # Ensure temporary files are removed even if exceptions occur
        if os.path.exists(mp3_file):
            os.remove(mp3_file)
        if os.path.exists(wav_file):
            os.remove(wav_file)

if __name__ == "__main__":
    import asyncio
    text_to_speak = "Hello, world! This is a test using Edge TTS."
    asyncio.run(speak_text(text_to_speak))