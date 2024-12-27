import os
import json
from .handlers.langchain_handler import LangChainHandler  # Changed to use LangChainHandler
from .utils.utils import speak  # Changed to relative import
import asyncio

class Assistant:
    def __init__(self, text="", lang='en'):
        """ Initialize the Assistant """
        self.text = text
        self.lang = lang
        self.langchain_handler = LangChainHandler(selected_language=lang)
        self.basic_chat_patterns = {
            'greetings': ['hey', 'hello', 'hi', 'bonjour', 'salam', 'mrhba'],
            'farewells': ['bye', 'goodbye', 'au revoir', 'bslama']
        }

    async def generate_speech(self):
        """ Generate speech from text """
        await speak(self.text, self.lang)

    async def play_speech(self):
        try:
            await self.generate_speech()
        except Exception as e:
            print(f"Error during playback: {e}")

    def change_language(self, lang):
        """ Change the language of the speech """
        self.lang = lang
        self.langchain_handler.selected_language = lang
        return self.lang

    def is_basic_chat(self, text):
        """Check if the input includes a basic chat interaction keyword"""
        text = text.lower().strip()
        for category, patterns in self.basic_chat_patterns.items():
            if any(pattern in text for pattern in patterns):
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

