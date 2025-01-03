import os
import json
import edge_tts
from .handlers.langchain_handler import LangChainHandler
from .utils.utils import speak
import asyncio

class Assistant:
    def __init__(self, text="", lang='en'):
        """ Initialize the Assistant """
        self.text = text
        self.lang = lang
        self.langchain_handler = LangChainHandler(selected_language=lang)
        
        # Pre-initialize TTS voices
        self.voice_names = {
            'en': 'en-US-EmmaMultilingualNeural',
            'fr': 'fr-FR-DeniseNeural',
            'ar': 'ar-MA-MounaNeural'
        }
        self.voices = {
            'en': edge_tts.Communicate(text="", voice=self.voice_names['en']),
            'fr': edge_tts.Communicate(text="", voice=self.voice_names['fr']),
            'ar': edge_tts.Communicate(text="", voice=self.voice_names['ar'])
        }
        
        self.basic_chat_patterns = {
            'greetings': ['hey.', 'hello.', 'hi.', 'bonjour.', 'salam.', 'mrhba.'],
            'farewells': ['bye.', 'goodbye.', 'au revoir.', 'bslama.']
        }

    async def generate_speech(self):
        """ Generate speech from text using pre-initialized voice """
        output_file = "temp.mp3"
        try:
            # Re-initialize the Communicate object with the current text
            self.voices[self.lang] = edge_tts.Communicate(text=self.text, voice=self.voice_names[self.lang])
            await self.voices[self.lang].save(output_file)
            
            # Play audio
            command = f'mpv --no-terminal {output_file}'
            # command = fr'"C:\Users\Home\Downloads\mpv-i686-w64-mingw32\mpv.exe" {output_file}'
            os.system(command)
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    async def play_speech(self):
        try:
            await self.generate_speech()
        except Exception as e:
            print(f"Error during playback: {e}")

    def change_language(self, lang):
        """ Change the language of the speech """
        if lang in self.voices:
            self.lang = lang
            self.langchain_handler.selected_language = lang
        return self.lang

    def is_basic_chat(self, text):
        """Check if the input includes a basic chat interaction keyword"""
        text = text.lower().strip()
        for category, patterns in self.basic_chat_patterns.items():
            if text in set(patterns):
                return category
        return None

    def get_basic_response(self, text):
        """Handle basic chat interactions"""
        category = self.is_basic_chat(text)
        if category == 'greetings':
            if self.lang == 'fr':
                return "Bonjour! Comment puis-je vous aider?"
            # elif self.lang in ['ar', 'ara']:
            #     return "مرحبا! كيف يمكنني مساعدتك؟"
            elif self.lang == 'ar':
                return "سلام! كيفاش نعاونك؟"
            else:
                return "Hello! How can I help you?"
        elif category == 'farewells':
            if self.lang == 'fr':
                return "Au revoir! À bientôt!"
            # elif self.lang in ['ar', 'ara']:
            #     return "مع السلامة! أراك قريبا!"
            elif self.lang == 'ar':
                return "بسلامة! نشوفك قريبا!"
            else:
                return "Goodbye! See you soon!"

    def get_response(self, question):
        """ Get a response to a question """
        if self.is_basic_chat(question):
            return self.get_basic_response(question)
        
        # Use LangChainHandler for dynamic response
        response = self.langchain_handler.get_response(question)
        return response['answer']

