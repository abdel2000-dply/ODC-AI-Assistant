from langchain_cohere import ChatCohere
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from src.utils.document_processor import DocumentProcessor
import os
from dotenv import load_dotenv

class LangChainHandler:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('COHERE_API_KEY')
        
        # Initialize the chat model
        self.llm = ChatCohere(
            cohere_api_key=self.api_key,
            temperature=0.3,
            max_tokens=512,
            model="command"  # Using command model for better chat performance
        )
        
        # Initialize vector store
        self.vector_store = DocumentProcessor.load_vector_store()
        
        # Create a custom prompt template
        prompt_template = """Use the following conversation history and context to answer the question.
        
Context: {context}
Chat History: {chat_history}
Question: {question}

Answer:"""
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="answer",
            return_messages=True,
            input_key="question"
        )
        
        # Create retrieval chain with custom prompt
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(),
            memory=self.memory,
            combine_docs_chain_kwargs={
                "prompt": PromptTemplate(
                    template=prompt_template,
                    input_variables=["context", "chat_history", "question"]
                )
            },
            return_source_documents=True,
            chain_type="stuff",
            verbose=True
        )

    def get_response(self, question, context=""):
        try:
            response = self.chain({"question": question})
            return {
                "answer": response.get("answer", "No answer generated"),
                "sources": [doc.metadata.get('source', 'Unknown') 
                          for doc in response.get("source_documents", [])]
            }
        except Exception as e:
            print(f"Error getting response: {e}")
            return {"answer": "Sorry, I encountered an error.", "sources": []}

if __name__ == "__main__":
    handler = LangChainHandler()
    print("\nODC AI Assistant (powered by LangChain)")
    print("Type 'quit' or 'exit' to end the conversation")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
                
            response = handler.get_response(user_input)
            print("\nAssistant:", response['answer'])
            if response['sources']:
                print("\nSources:", ", ".join(response['sources']))
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Let's continue our conversation...")
