from gtts import gTTS
import os
from transformers import pipeline


class Assistant:
    def __init__(self, text, lang='en'):
        """ Initialize the Assistant """
        self.text = text
        self.lang = lang
        self.generator = pipeline('text-generation', model='gpt2')
        self.qa_model = pipeline('question-answering', model='mrm8488/bert-tiny-5-finetuned-squadv2')

    def generate_speech(self):
        """ Generate speech from text """
        output_file = "output.mp3"
        tts = gTTS(text=self.text, lang=self.lang)
        tts.save(output_file)
        return output_file

    def play_speech(self):
        """ Play the speech """
        output_file = self.generate_speech()
        os.system(f"mpg321 {output_file}")

    def change_language(self, lang):
        """ Change the language of the speech """
        self.lang = lang
        return self.lang

    def ask_AI(self, prompt):
        """ Ask AI a question and get a response """
        response = self.generator(prompt, max_length=50, num_return_sequences=1, truncation=True)
        return response[0]['generated_text'].strip()

    def ask_factual_question(self, question, context):
        """ Ask a factual question and get a response """
        result = self.qa_model(question=question, context=context)
        return result['answer']

