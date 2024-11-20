import pyttsx3

def test_pyttsx3_espeak():
    """Tests pyttsx3 with Espeak, allowing voice selection and parameter adjustment."""

    engine = pyttsx3.init(driverName='espeak')

    # List available voices with their names
    voices = engine.getProperty('voices')
    for index, voice in enumerate(voices):
        print(f"Voice {index}: {voice.name}")

    # Select a voice (adjust the index based on your preference)
    engine.setProperty('voice', voices[1].id)  # Adjust the index (0-based)

    # Set speech parameters (optional)
    engine.setProperty('rate', 150)  # Adjust speaking rate
    engine.setProperty('volume', 1.0)  # Adjust volume

    # Text to speech
    text = "This is a test to improve Espeak's voice quality."
    engine.say(text)
    engine.runAndWait()

def test_espeak_standalone(text):
    """Uses the Espeak command-line tool directly, offering more control."""

    # Modify these options according to your preferences
    espeak_command = f'espeak -s 150 -v en-us "{text}"'  # Set voice (en-us) and rate (150)

    # Execute Espeak command
    import subprocess
    subprocess.run(espeak_command.split())  # Ensure text is properly escaped

# def test_festival_standalone(text):
#     """Tests the Festival text-to-speech engine (requires installation)."""

#     # Install Festival if not already installed: `sudo apt-get install festival`
#     import festival

#     # Set voice and other parameters (consult Festival documentation)
#     festival.Festival(tts="samantha")  # Example voice (modify as needed)

#     festival.tts(text)

# Example usage (uncomment desired tests)
if __name__ == "__main__":
    # test_pyttsx3_espeak()  # Test pyttsx3 with Espeak
    test_espeak_standalone("This is a test using Espeak directly.")
    # test_festival_standalone("This is a test using Festival TTS.")