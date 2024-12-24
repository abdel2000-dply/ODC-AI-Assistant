from langchain_cohere import ChatCohere
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from src.utils.document_processor import DocumentProcessor
import os
from dotenv import load_dotenv
from langdetect import detect

class LangChainHandler:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('COHERE_API_KEY')
        
        self.llm = ChatCohere(
            cohere_api_key=self.api_key,
            temperature=0.3,
            max_tokens=512,
            model="command-r-plus-08-2024"
        )
        
        self.vector_store = DocumentProcessor.load_vector_store()
        
        # Updated prompt template with language and style guidelines
        prompt_template = """You are a friendly and professional AI Assistant. Answer directly and concisely.
Always respond in the same language as the user's question. If the source content is in a different language,
translate the information but don't mention the original language.

System Role: Provide clear, direct answers while maintaining a helpful and professional tone.

Language Guidelines:
- For English: Be clear and professional
- For French: Use formal French ("vous")
- For Arabic/Darija: Use conversational, respectful tone
- Always match the user's language choice

Context: {context}
Chat History: {chat_history}
Question: {question}

Answer:"""
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="answer",
            return_messages=True,
            input_key="question"
        )
        
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
        
        self.clear_memory()  # Clear memory on initialization

        self.basic_chat_patterns = {
            'greetings': ['hey', 'hello', 'hi', 'bonjour', 'salam', 'mrhba'],
            'farewells': ['bye', 'goodbye', 'au revoir', 'bslama']
        }

    def clear_memory(self):
        """Clear the conversation memory"""
        if hasattr(self, 'memory'):
            self.memory.clear()
        if hasattr(self, 'chain'):
            self.chain.memory.clear()

    def detect_language(self, text):
        try:
            lang = detect(text)
            return lang
        except:
            return 'en'  # Default to English if detection fails

    def is_basic_chat(self, text):
        """Check if the input is a basic chat interaction"""
        text = text.lower().strip()
        return any(text in patterns for patterns in self.basic_chat_patterns.values())

    def get_basic_response(self, text, lang):
        """Handle basic chat interactions"""
        if lang == 'fr':
            return "Bonjour! Comment puis-je vous aider?"
        elif lang in ['ar', 'ara']:
            return "مرحبا! كيف يمكنني مساعدتك؟"
        else:
            return "Hello! How can I help you?"

    def get_response(self, question, context=""):
        try:
            lang = self.detect_language(question)
            
            # Handle basic chat without using the retriever
            if self.is_basic_chat(question):
                return {
                    "answer": self.get_basic_response(question, lang),
                    "sources": []
                }
            
            # Use retriever for content-related queries
            response = self.chain.invoke({
                "question": question,
                "language": lang
            })
            
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
    print("Type 'quit', 'exit' to end or 'clear' to reset memory")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                handler.clear_memory()
                print("Memory cleared!")
                continue
            
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
