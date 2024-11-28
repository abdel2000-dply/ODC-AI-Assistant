import cohere
import os
import requests
import json
from dotenv import load_dotenv

class DynamicHandler:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv('COHERE_API_KEY')
        self.client = cohere.Client(self.api_key)
        self.chat_api_endpoint = "https://api.cohere.com/v1/chat"
        self.chat_history = []

        # Load the ODC info from the JSON file
        with open("src/pre_dynamic_context.json", "r") as file:
            self.odc_info = json.load(file)

    def chat_with_cohere(self, message):
        headers = {
            "Authorization": f"BEARER {self.api_key}",
            "Content-Type": "application/json",
        }

        # Limit the chat history to the last 5 messages
        limited_chat_history = self.chat_history[-5:]

        data = {
            "message": message,
            "chat_history": [{"role": entry["role"], "content": entry["content"], "message": entry["content"]} for entry in limited_chat_history],
            "max_tokens": 50,  # Set a lower value for shorter responses
            "temperature": 0.2,  # Lower temperature for more direct responses
            "context": {
                "odc_info": self.odc_info
            }
        }

        response = requests.post(self.chat_api_endpoint, json=data, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            generated_response = response_data["text"]
            self.chat_history.append({"role": "user", "content": message, "message": message})
            self.chat_history.append({"role": "chatbot", "content": generated_response, "message": generated_response})
            return generated_response
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def get_response(self, question, context):
        return self.chat_with_cohere(question)