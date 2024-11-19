from transformers import pipeline, DistilBertTokenizer, DistilBertForQuestionAnswering

class DynamicHandler:
    def __init__(self):
        self.tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-distilled-squad")
        self.qa_model = DistilBertForQuestionAnswering.from_pretrained("distilbert-base-uncased-distilled-squad")
        self.qa_pipeline = pipeline("question-answering", model=self.qa_model, tokenizer=self.tokenizer)

    def get_response(self, question, context):
        result = self.qa_pipeline(question=question, context=context)
        return result['answer']