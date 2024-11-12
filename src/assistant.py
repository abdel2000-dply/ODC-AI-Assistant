from gtts import gTTS
import os

class Assistant:
    def __init__(self, text, lang='en'):
        """ Initialize the Assistant
        """
        self.text = text
        self.lang = lang

    def generate_speech(self):
        """ Generate speech from text
        """
        output_file = "output.mp3"
        tts = gTTS(text=self.text, lang=self.lang)
        tts.save(output_file)
        return output_file

    def play_speech(self):
        """ Play the speech
        """
        output_file = self.generate_speech()
        os.system(f"start {output_file}")
        # delete the file after playing
        os.remove(output_file)

    def change_language(self, lang):
        """ Change the language of the speech
        """
        self.lang = lang
        return self.lang

