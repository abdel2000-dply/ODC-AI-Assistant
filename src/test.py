import os
import edge_tts
import pyaudio
import wave

async def speak_text(text):
    """Speaks the given text using Edge TTS and plays it directly."""
    voice = 'en-US-AndrewMultilingualNeural'  # Adjust voice as needed
    audio_file = 'temp.wav'

    try:
        # Generate speech using edge-tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(audio_file)

        # Play the audio file using pyaudio
        wf = wave.open(audio_file, 'rb')
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
        # Ensure temporary file is removed even if exceptions occur
        if os.path.exists(audio_file):
            os.remove(audio_file)

if __name__ == "__main__":
    import asyncio
    text_to_speak = "Hello, world! This is a test using Edge TTS."
    asyncio.run(speak_text(text_to_speak))