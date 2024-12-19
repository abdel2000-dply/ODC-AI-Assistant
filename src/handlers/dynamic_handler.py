import cohere
import os
import requests
from dotenv import load_dotenv
from src.utils.document_processor import DocumentProcessor  # Changed from relative to absolute import

class DynamicHandler:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('COHERE_API_KEY')
        self.client = cohere.Client(self.api_key)
        self.chat_history = []
        self.chat_api_endpoint = "https://api.cohere.ai/v1/chat"  # Added missing endpoint
        
        # Initialize vector store with better error handling
        try:
            self.vector_store = DocumentProcessor.load_vector_store()
            if not self.vector_store:
                print("Warning: Vector store not initialized. Running setup first...")
                processor = DocumentProcessor()
                self.vector_store = processor.process_documents()
        except Exception as e:
            print(f"Error loading vector store: {e}")
            print("Please run setup.py first to initialize the vector store")
            self.vector_store = None

    def get_relevant_context(self, question, k=3):
        if not self.vector_store:
            print("Warning: Vector store not available")
            return ""
        try:
            docs = self.vector_store.similarity_search(question, k=k)
            return "\n".join(doc.page_content for doc in docs)
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return ""

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