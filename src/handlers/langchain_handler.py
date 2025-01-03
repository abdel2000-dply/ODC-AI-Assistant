from langchain_cohere import ChatCohere
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from src.utils.document_processor import DocumentProcessor
import os
from dotenv import load_dotenv
from langchain.chains import LLMChain

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
        
        # RAG specific LLM
        self.llm_rag = ChatCohere(
            cohere_api_key=self.api_key,
            temperature=0.3,
            max_tokens=300,
            model="command-r-plus-08-2024"
        )
        
        # General LLM (using Cohere LLM)
        self.llm_general = ChatCohere(
            cohere_api_key=self.api_key,
            temperature=0.5,
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
        - Respond in the selected language regardless of the context language (IMPORTANT).
        - Respond ONLY in the specified language
        - Be direct and brief (1-3 sentences)
        - Try to minimize the number of words in the response and when there is more to say wait or request(not always) if the user wants more details on that matter
        - Include relevant technical details only when asked.
        - Ignore irrelevant context from the chat history
        - If the language is Moroccan Darija respond in moroccan darija not general arabic.
        - The Question could have a typo, respond to the best of your understanding like the question could be about orange digital center.
        - If the question contains digital center I mean Orange digital center the word befor could be a tyepo.

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
        
        # Custom retriever with control over number of results (k)
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm_rag, # RAG Specific LLM
            retriever=retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={
                "prompt": PromptTemplate(
                    template=prompt_template,
                    input_variables=["context", "chat_history", "question"]
                )
            },
            return_source_documents=True,
            chain_type="stuff",
            # question_generator=None, # set to None for no standalone question generation
            # verbose=True
        )
        
        general_prompt_template = """You are a friendly and professional AI Assistant. 
        You must ALWAYS respond in a helpful and professional tone.
        Be as brief as possible and avoid unnecessary details, remember it's a conversation so short and direct answers are preferred to keep a conversation.

        Guidelines:
        - Be direct and brief (1-3 sentences)
        - Try to minimize the number of words in the response and when there is more to say request if the user wants more details on that matter
        - Include relevant technical details only when asked.
        - Ignore irrelevant context from the chat history

        Question: {question}

        Answer:"""
        
        # General LLM chain for questions not on the context of the fablab
        self.general_chain = LLMChain(
            llm=self.llm_general,
            prompt=PromptTemplate(template=general_prompt_template),
            # verbose=True
        )

        self.clear_memory()  # Clear memory on initialization

        # classification prompt
        self.classification_prompt = """
        You are a classifier that analyzes a question and categorizes it into one of these three categories:
            - RAG_RELEVANT: The question is related to the Orange Digital Center and it can be answered with the FabLab context.
            - GENERAL_KNOWLEDGE: The question is general and not related to the Orange Digital Center.
            - UNCLEAR: It is not clear if the question is related to the Orange Digital Center.

        Guidelines:
        - If the question mentions specific programs, events, Trainings, registarion, materials, support, or facilities at the Orange Digital Center, classify it as RAG_RELEVANT.
        - If the question is about general knowledge or unrelated topics, classify it as GENERAL_KNOWLEDGE.
        - If the question is ambiguous or lacks enough context to determine its relevance, classify it as UNCLEAR.

        Examples:
        - "What programs does the Orange Digital Center offer?" -> RAG_RELEVANT
        - "How do I learn to code?" -> GENERAL_KNOWLEDGE
        - "Can you tell me more about the center?" -> UNCLEAR

        Question: {question}
        Category:
        """

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
    
    def classify_question(self, question):
        """Classifies the input question as RAG_RELEVANT, GENERAL_KNOWLEDGE or UNCLEAR"""
        try:
            classification_chain = LLMChain(llm = self.llm_general, prompt=PromptTemplate(template=self.classification_prompt))
            response = classification_chain.invoke({"question": question})
            classification = response['text'].strip()
            return classification
        except Exception as e:
            return "UNCLEAR"

    def get_response(self, question, context=""):
        try:
            classification = self.classify_question(question)

            if classification == "RAG_RELEVANT":
                memory_variables = self.memory.load_memory_variables({})
                chat_history = memory_variables.get("chat_history", "")
                response = self.chain.invoke({
                    "question": question,
                    "language": self.selected_language
                })
                return {
                    "answer": response.get("answer", "No answer generated"),
                    "sources": [doc.metadata.get('source', 'Unknown')
                            for doc in response.get("source_documents", [])]
                }
            elif classification == "GENERAL_KNOWLEDGE":
                response = self.general_chain.invoke({"question": question})
                return {"answer": response['text'], "sources": []}
            else:
                 fallback_messages = {
                    'en': "I'm not sure what you mean. Can you please ask another question about FabLab Orange Digital Center?",
                    'fr': "Je ne suis pas sûr de ce que vous voulez dire. Pouvez-vous poser une autre question sur FabLab Orange Digital Center?",
                    'ar': "مفهمتش سؤالك مزيان. ممكن تسول شي سؤال آخر على FabLab Orange Digital Center؟"
                }
                 return {"answer": fallback_messages.get(self.selected_language, fallback_messages['en']), "sources": []}
        except Exception as e:
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