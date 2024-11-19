from gtts import gTTS
import os
import json
from transformers import pipeline
from handlers.static_handler import StaticHandler
from handlers.pre_dynamic_handler import PreDynamicHandler
from handlers.dynamic_handler import DynamicHandler


class Assistant:
    def __init__(self, text="", lang='en', static_responses_file='src/static_responses.json', pre_dynamic_context_file='src/pre_dynamic_context.json'):
        """ Initialize the Assistant """
        self.text = text
        self.lang = lang
        self.static_handler = StaticHandler(static_responses_file)
        self.pre_dynamic_handler = PreDynamicHandler()
        self.dynamic_handler = DynamicHandler()
        
        # Load pre-dynamic context from JSON file
        with open(pre_dynamic_context_file, 'r') as file:
            self.pre_dynamic_context = json.load(file)

    def generate_speech(self):
        """ Generate speech from text """
        output_file = "output.mp3"
        tts = gTTS(text=self.text, lang=self.lang)
        tts.save(output_file)
        return output_file

    def play_speech(self):
        try:
            output_file = self.generate_speech()
            os.system(f"mpg321 {output_file}")
        except Exception as e:
            print(f"Error during playback: {e}")

    def change_language(self, lang):
        """ Change the language of the speech """
        self.lang = lang
        return self.lang

    def get_response(self, question):
        """ Get a response to a question """
        # Check for static response
        static_response = self.static_handler.get_response(question)
        if static_response:
            return static_response
        
        # Check for pre-dynamic context
        # if question in self.pre_dynamic_context:
        context = self.pre_dynamic_context.get('context')
        return self.pre_dynamic_handler.get_response(question, context)
        
        # Use dynamic model
        # return self.dynamic_handler.get_response(question, context=None)

