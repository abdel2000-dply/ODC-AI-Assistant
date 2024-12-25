import asyncio
from .assistant import Assistant  # Change to relative import
from .utils.utils import recognize_speech_from_mic  # Change to relative import

async def main():
    # Initialize the Assistant with a greeting message
    assistant = Assistant("Hello, I'm Orange Digital Center's Assistant. How can I help you?")
    await assistant.play_speech()

    while True:
        # Recognize speech from the microphone
        question = None
        while not question:
            question = recognize_speech_from_mic()

        # Check for exit condition
        if question.lower() in ["exit", "quit", "goodbye", "bye", "stop", "bslama", "au revoir"]:
            assistant.text = "Goodbye!"
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
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    
    asyncio.run(main())