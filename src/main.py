from assistant import Assistant
from utils import recognize_speech_from_mic
import asyncio

# Initialize the Assistant with a greeting message
assistant = Assistant("Hello, I'm Orange Digital Center's Assistant. How can I help you?")
asyncio.run(assistant.play_speech())

while True:
    # Recognize speech from the microphone
    question = recognize_speech_from_mic()

    # Check for exit condition
    if question is None or question.lower() in ["exit", "quit"]:
        assistant.text = "Goodbye!"
        asyncio.run(assistant.play_speech())
        break

    print(f"Question: {question}")

    # Get the response
    response = assistant.get_response(question)
    print(f"Response: {response}")

    # Update the text and play the response
    assistant.text = response
    asyncio.run(assistant.play_speech())