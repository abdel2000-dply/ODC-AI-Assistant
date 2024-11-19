from assistant import Assistant
from utils import recognize_speech_from_mic

# Initialize the Assistant with a hey message
assistant = Assistant("Hello, I'm Orange digital Center's Assistant. How can I help you?")
assistant.play_speech()

# # Recognize speech from the microphone
# question = recognize_speech_from_mic()

question = "what is this place?"
print(f"Question: {question}")

# Get the response
response = assistant.get_response(question)
print(f"Response: {response}")

# Generate and play the response
assistant.text = response
assistant.play_speech()