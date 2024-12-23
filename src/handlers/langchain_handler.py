from langchain.llms import Cohere
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from ..utils.document_processor import DocumentProcessor  # Changed to relative import
import os
from dotenv import load_dotenv

class LangChainHandler:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('COHERE_API_KEY')
        
        # Initialize the language model
        self.llm = Cohere(
            cohere_api_key=self.api_key,
            temperature=0.3,
            max_tokens=512
        )
        
        # Initialize vector store
        self.vector_store = DocumentProcessor.load_vector_store()
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create retrieval chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(),
            memory=self.memory,
            return_source_documents=True,
            max_tokens_limit=3000
        )

    def get_response(self, question, context=""):
        try:
            response = self.chain({"question": question})
            return {
                "answer": response["answer"],
                "sources": [doc.metadata.get('source', 'Unknown') 
                          for doc in response.get("source_documents", [])]
            }
        except Exception as e:
            print(f"Error getting response: {e}")
            return {"answer": "Sorry, I encountered an error.", "sources": []}

if __name__ == "__main__":
    # Test the LangChain handler
    handler = LangChainHandler()
    test_questions = [
        "What is Orange Digital Center?",
        "What programs are available at ODC?",
        "Tell me about the coding school",
        "What is FabLab?",
    ]
    
    print("\nTesting LangChain Handler:")
    print("-" * 50)
    
    for question in test_questions:
        print(f"\nQ: {question}")
        response = handler.get_response(question)
        print(f"A: {response['answer']}")
        if response['sources']:
            print("Sources:", ", ".join(response['sources']))
        print("-" * 50)
