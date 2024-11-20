import os
import edge_tts
import pygame

async def speak_text(text):
    """Speaks the given text using Edge TTS and plays it directly."""
    voice = 'en-US-JennyNeural'  # Adjust voice as needed
    audio_file = 'temp.mp3'

    try:
        # Generate speech using edge-tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(audio_file)

        # Initialize pygame mixer
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)

        # Play the audio file
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Error during TTS or playback: {e}")  # Informative error message
    finally:
        # Ensure temporary file is removed even if exceptions occur
        if os.path.exists(audio_file):
            os.remove(audio_file)
        pygame.mixer.quit()

if __name__ == "__main__":
    import asyncio
    text_to_speak = "Hello, world! This is a test using Edge TTS."
    asyncio.run(speak_text(text_to_speak))