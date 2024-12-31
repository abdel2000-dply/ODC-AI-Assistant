import asyncio
import sys
from pathlib import Path
from src.assistant import Assistant  # Change to relative import
from src.utils.utils import recognize_speech_from_mic, record_audio_to_file, transcribe_audio_with_groq  # Updated imports
import tkinter as tk

async def assistant_main(selected_language='en'):
    # Initialize the Assistant with a greeting message
    assistant = Assistant("Hello, I'm Orange Digital Center's Assistant. How can I help you?", lang=selected_language)
    await assistant.play_speech()

    while True:
        # Record and transcribe speech
        question = None
        while not question:
            record_audio_to_file()
            # question = transcribe_audio_with_groq(language=selected_language)
            question = None  # Remove this line after implementing transcribe_audio_with_groq
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

def main():
    root = tk.Tk()
    root.title("Main Application")
    root.geometry("800x600")
    root.configure(bg="white")

    label = tk.Label(root, text="This is the main application", font=("Monospace", 20), fg="black", bg="white")
    label.pack(expand=True)

    root.mainloop()

if __name__ == "__main__":
    # Add this to allow running from project root
    sys.path.append(str(Path(__file__).parent.parent))
    
    # Get the selected language from command line arguments
    selected_language = sys.argv[1] if len(sys.argv) > 1 else 'en'
    
    asyncio.run(assistant_main(selected_language))
    main()