import cohere
import os
from transformers import pipeline, DistilBertTokenizer, DistilBertForQuestionAnswering

class DynamicHandler:
    def __init__(self):
        self.api_key = os.getenv('COHERE_API_KEY')
        self.client = cohere.Client(self.api_key)
        self.tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-distilled-squad")
        self.qa_model = DistilBertForQuestionAnswering.from_pretrained("distilbert-base-uncased-distilled-squad")
        self.qa_pipeline = pipeline("question-answering", model=self.qa_model, tokenizer=self.tokenizer)

    def get_response(self, question, context):
        response = self.client.generate(
            model='xlarge',
            prompt=f"{context}\n\nQuestion: {question}\nAnswer:",
            max_tokens=50,
            temperature=0.7,
            k=0,
            stop_sequences=["\n"]
        )
        return response.generations[0].text.strip()