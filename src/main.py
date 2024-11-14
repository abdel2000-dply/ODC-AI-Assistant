from assistant import Assistant

# Initialize the Assistant with a greeting text
assistant = Assistant("Hello, world! This is a text-to-speech example.")

# Generate and play speech
assistant.play_speech()

# # Ask AI a question
# prompt = "What is the capital of France?"
# response = assistant.ask_AI(prompt)
# print(f"AI response: {response}")

# # Generate and play the AI response
# assistant.text = response
# assistant.play_speech()

# Ask a factual question
context = "France is a country in Europe. Paris is the capital of France."
question = "What is Paris?"
factual_response = assistant.ask_factual_question(question, context)
print(f"Factual response: {factual_response}")

# Generate and play the factual response
assistant.text = factual_response
assistant.play_speech()