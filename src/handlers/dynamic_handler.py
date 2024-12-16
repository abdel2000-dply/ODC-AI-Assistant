import cohere
import os
from dotenv import load_dotenv
from ..utils.document_processor import DocumentProcessor

class DynamicHandler:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('COHERE_API_KEY')
        self.client = cohere.Client(self.api_key)
        self.chat_history = []
        self.vector_store = DocumentProcessor.load_vector_store()

    def get_relevant_context(self, question, k=3):
        docs = self.vector_store.similarity_search(question, k=k)
        return "\n".join(doc.page_content for doc in docs)

    def chat_with_cohere(self, message):
        # Retrieve relevant context
        context = self.get_relevant_context(message)
        
        headers = {
            "Authorization": f"BEARER {self.api_key}",
            "Content-Type": "application/json",
        }

        limited_chat_history = self.chat_history[-5:]

        data = {
            "message": message,
            "chat_history": [{"role": entry["role"], "content": entry["content"]} for entry in limited_chat_history],
            "max_tokens": 150,
            "temperature": 0.3,
            "context": context
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