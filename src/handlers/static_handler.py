import json

class StaticHandler:
    def __init__(self, static_responses_file='static_responses.json'):
        with open(static_responses_file, 'r') as file:
            self.static_responses = json.load(file)

    def get_response(self, question):
        return self.static_responses.get(question)