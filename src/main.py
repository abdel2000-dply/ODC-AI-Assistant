from assistant import Assistant

text = "Hello, world! This is a text-to-speech example."

assistant = Assistant("Bonjour test test, merci", lang='fr')
assistant.play_speech()










# from gtts import gTTS
# import os

# # Text to be spoken
# text = "Hello, world! This is a text-to-speech example."

# # Generate speech
# tts = gTTS(text=text, lang='en')

# # Save the speech to a file
# tts.save("output.mp3")

# # Play the speech (this will work on Raspberry Pi)
# os.system("mpg321 output.mp3")