from langchain_cohere import ChatCohere
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from src.utils.document_processor import DocumentProcessor
import os
from dotenv import load_dotenv

class LangChainHandler:
    SUPPORTED_LANGUAGES = {
        '1': {'code': 'en', 'name': 'English'},
        '2': {'code': 'fr', 'name': 'French'},
        # '3': {'code': 'ar', 'name': 'Arabic/Darija'},
        '4': {'code': 'ar', 'name': 'Moroccan Darija'}
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
        
        self.vector_store = DocumentProcessor.load_vector_store()
        
        self.selected_language = selected_language
        self.greetings = {
            'en': "Hello! How can I help you?",
            'fr': "Bonjour! Comment puis-je vous aider?",
            # 'ar': "مرحبا! كيف يمكنني مساعدتك؟",
            'ar': "سلام! كيفاش نعاونك؟"
        }
        
        prompt_template = """You are a friendly and professional AI Assistant for Fablab Orange digital center. 
        You must ALWAYS respond in {language} language regardless of the content language.
        Maintain a helpful and professional tone.
        Be as brief as possible and avoid unnecessary details, remember it's a conversation so short and direct answers are preferred to keep a conversation.

        Guidelines:
        - If the question is a basic chat interaction, respond with a greeting or farewell, don't depend on the context just request if you could assist with anything related to Fablab Orange digital center
        - Respond ONLY in the specified language
        - Be direct and brief (2-3 sentences)
        - Avoid unnecessary details
        - Try to minimize the number of words in the response and when there is more to say request if the user wants more details on that matter
        - Provide specific examples when relevant
        - If unsure, acknowledge limitations
        - Include relevant technical details only when asked
        - Ignore irrelevant context from the chat history
        - Respond in the selected language regardless of the context language
        - If the language is Moroccan Darija respond in moroccan darija not general arabic

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

    @classmethod
    def select_language(cls):
        print("\nPlease select your preferred language:")
        for key, lang in cls.SUPPORTED_LANGUAGES.items():
            print(f"{key}. {lang['name']}")
        
        while True:
            choice = input("Enter your choice (1-4): ").strip()
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
        # elif lang in ['ar', 'ara']:
        #     return "مرحبا! كيف يمكنني مساعدتك؟"
        elif lang == 'ar':
            return "سلام! كيفاش نعاونك؟"
        else:
            return "Hello! How can I help you?"

    def rephrase_to_standalone(self, follow_up_question, chat_history):
        """Rephrase the follow-up question to be a standalone question"""
        try:
            rephrase_prompt = f"""Given the following conversation and a follow-up question, rephrase the follow-up question to be a standalone question, in its original language, but dont change the question to something else.

            Chat History:
            {chat_history}

            Follow Up Input: {follow_up_question}
            Standalone question:"""
            
            response = self.llm.generate(rephrase_prompt)
            return response['choices'][0]['text'].strip()
        except Exception as e:
            print(f"Error rephrasing question: {e}")
            return follow_up_question

    def get_response(self, question, context=""):
        try:
            memory_variables = self.memory.load_memory_variables({})
            chat_history = memory_variables.get("chat_history", "")
            # standalone_question = self.rephrase_to_standalone(question, chat_history)
            response = self.chain.invoke({
                "question": question,  # Use the question directly
                "language": self.selected_language
            })
            
            return {
                "answer": response.get("answer", "No answer generated"),
                "sources": [doc.metadata.get('source', 'Unknown') 
                          for doc in response.get("source_documents", [])]
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

            if handler.is_basic_chat(user_input):
                response = handler.get_basic_response(user_input, handler.selected_language)
                print("\nAssistant:", response)
            else:
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