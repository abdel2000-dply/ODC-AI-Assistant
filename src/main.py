import asyncio
import sys
from pathlib import Path
from .assistant import Assistant  # Change to relative import
from .utils.utils import recognize_speech_from_mic, record_audio_to_file, transcribe_audio_with_groq  # Updated imports

async def main(selected_language):
    # Initialize the Assistant with a greeting message
    assistant = Assistant("Hello, I'm Orange Digital Center's Assistant. How can I help you?", lang=selected_language)
    await assistant.play_speech()

    while True:
        # Record and transcribe speech
        question = None
        while not question:
            record_audio_to_file()
            question = transcribe_audio_with_groq(language=selected_language)
            if not question:
                print("Falling back to speech_recognition...")
                question = recognize_speech_from_mic(language=selected_language)

        # Check for exit condition
        if any(exit_phrase in question.lower() for exit_phrase in ["exit", "quit", "goodbye", "bye", "stop", "bslama", "au revoir", "مع السلامة", "وداعا", "بسلامة"]):
            assistant.text = "Goodbye! See you soon!"
            await assistant.play_speech()
            break

        print(f"Question: {question}")

        # Get the response
        response = assistant.get_response(question)
        print(f"Response: {response}")

        # Update the text and play the response
        assistant.text = response
        await assistant.play_speech()

if __name__ == "__main__":
    # Add this to allow running from project root
    sys.path.append(str(Path(__file__).parent.parent))
    
    # Get the selected language from command line arguments
    selected_language = sys.argv[1] if len(sys.argv) > 1 else 'en'
    
    asyncio.run(main(selected_language))