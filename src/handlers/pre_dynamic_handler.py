from transformers import pipeline

class PreDynamicHandler:
    def __init__(self):
        self.qa_model = pipeline('question-answering', model='mrm8488/bert-tiny-5-finetuned-squadv2')

    def get_response(self, question, context):
        result = self.qa_model(question=question, context=context)
        return result['answer']