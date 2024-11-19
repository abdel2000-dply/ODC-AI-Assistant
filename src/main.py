from assistant import Assistant
from utils import recognize_speech_from_mic

# Initialize the Assistant with a greeting message
assistant = Assistant("Hello, I'm Orange Digital Center's Assistant. How can I help you?")
assistant.play_speech()

while True:
    # Recognize speech from the microphone
    question = recognize_speech_from_mic()

    # Check for exit condition
    if question.lower() in ["exit", "quit"]:
        assistant.text = "Goodbye!"
        assistant.play_speech()
        break

    print(f"Question: {question}")

    # Get the response
    response = assistant.get_response(question)
    print(f"Response: {response}")

    # Generate and play the response
    assistant.text = response
    assistant.play_speech()