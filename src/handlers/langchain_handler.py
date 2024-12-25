from langchain_cohere import ChatCohere
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, RunnablePassthrough, OpenAIFunctionsAgentOutputParser
from src.utils.document_processor import DocumentProcessor
import os
from dotenv import load_dotenv

class LangChainHandler:
    SUPPORTED_LANGUAGES = {
        '1': {'code': 'en', 'name': 'English'},
        '2': {'code': 'fr', 'name': 'French'},
        '3': {'code': 'ar', 'name': 'Arabic/Darija'}
    }

    def __init__(self, selected_language='en'):
        load_dotenv()
        self.api_key = os.getenv('COHERE_API_KEY')
        
        self.llm = ChatCohere(
            cohere_api_key=self.api_key,
            temperature=0.3,
            max_tokens=300,
            model="command-r-plus-08-2024"
        )
        
        # Configure retriever with specific parameters
        self.vector_store = DocumentProcessor.load_vector_store()
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 3,  # Number of documents to retrieve
                "score_threshold": 0.5  # Minimum similarity score (0-1)
            }
        )
        
        self.selected_language = selected_language
        self.greetings = {
            'en': "Hello! How can I help you?",
            'fr': "Bonjour! Comment puis-je vous aider?",
            'ar': "مرحبا! كيف يمكنني مساعدتك؟"
        }
        
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful but sassy assistant"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self.chain = RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_to_openai_functions(x["intermediate_steps"])
        ) | self.prompt | self.llm | OpenAIFunctionsAgentOutputParser()
        
        self.qa = AgentExecutor(agent=self.chain, tools=[], verbose=False, memory=self.memory)
        
        self.clear_memory()  # Clear memory on initialization

        self.basic_chat_patterns = {
            'greetings': ['hey', 'hello', 'hi', 'bonjour', 'salam', 'mrhba'],
            'farewells': ['bye', 'goodbye', 'au revoir', 'bslama']
        }

    @classmethod
    def select_language(cls):
        print("\nPlease select your preferred language:")
        for key, lang in cls.SUPPORTED_LANGUAGES.items():
            print(f"{key}. {lang['name']}")
        
        while True:
            choice = input("Enter your choice (1-3): ").strip()
            if choice in cls.SUPPORTED_LANGUAGES:
                return cls.SUPPORTED_LANGUAGES[choice]['code']
            print("Invalid choice, please try again.")

    def clear_memory(self):
        """Clear the conversation memory"""
        if hasattr(self, 'memory'):
            self.memory.clear()
        if hasattr(self, 'chain'):
            self.chain.memory.clear()

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
            # Add debug info about retrieved documents
            response = self.qa.invoke({
                "input": question,
                "context": context
            })
            
            sources = response.get("source_documents", [])
            
            if self.chain.verbose:
                print(f"\nRetrieved {len(sources)} relevant documents")
                for i, doc in enumerate(sources, 1):
                    print(f"Doc {i} score: {doc.metadata.get('score', 'N/A')}")
            
            return {
                "answer": response.get("answer", "No answer generated"),
                "sources": [doc.metadata.get('source', 'Unknown') for doc in sources]
            }
        except Exception as e:
            print(f"Error getting response: {e}")
            error_messages = {
                'en': "Sorry, I encountered an error.",
                'fr': "Désolé, j'ai rencontré une erreur.",
                'ar': "عذراً، حدث خطأ ما."
            }
            return {"answer": error_messages.get(self.selected_language, error_messages['en']), "sources": []}

if __name__ == "__main__":
    # Get language preference at startup
    selected_language = LangChainHandler.select_language()
    handler = LangChainHandler(selected_language)
    
    welcome_messages = {
        'en': "\nODC AI Assistant (powered by LangChain)\nType 'quit', 'exit' to end or 'clear' to reset memory",
        'fr': "\nAssistant IA ODC (propulsé par LangChain)\nTapez 'quit', 'exit' pour terminer ou 'clear' pour réinitialiser",
        'ar': "\nمساعد ODC الذكي\nاكتب 'quit' أو 'exit' للخروج أو 'clear' لمسح المحادثة"
    }
    
    print(welcome_messages.get(selected_language, welcome_messages['en']))
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
