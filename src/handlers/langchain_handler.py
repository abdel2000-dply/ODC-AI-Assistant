import re
from fuzzywuzzy import fuzz  # Import fuzzywuzzy
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from src.utils.document_processor import DocumentProcessor
from langchain import verbose
import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any

verbose = True

class LangChainHandler:
    SUPPORTED_LANGUAGES = {
        '1': {'code': 'en', 'name': 'English'},
        '2': {'code': 'fr', 'name': 'French'},
        # '3': {'code': 'ar', 'name': 'Arabic/Darija'},
        '4': {'code': 'ar', 'name': 'Moroccan Darija'}
    }

    def __init__(self, selected_language='en'):
        load_dotenv()
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        # RAG specific LLM
        self.llm_rag = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            api_key = self.api_key,
            verbose=True
        )
        
        # General LLM 
        self.llm_general = ChatGoogleGenerativeAI(
             model="gemini-2.0-flash",
             temperature=0.5,
             api_key=self.api_key
        )
        
        self.vector_store = DocumentProcessor.load_vector_store()

        if self.vector_store is None:
            raise ValueError("Failed to load vector store. Please check the DocumentProcessor configuration.")
        
        self.selected_language = selected_language
        self.greetings = {
            'en': "Hello! How can I help you?",
            'fr': "Bonjour! Comment puis-je vous aider?",
            'ar': "سلام! كيفاش نعاونك؟"
        }
        
        rag_prompt_template = """
        You are ODC AI Assistant, a helpful AI assistant for the Orange Digital Center.  Your goal is to provide accurate, concise information about ODC programs, resources, and opportunities.
        Respond in {language}, translating if needed. Prioritize information from the 'Context'.
        Adopt a friendly and informative tone, like a helpful colleague.  Answer in a single paragraph (5-7 sentences max).  Do NOT use bullet points or special characters.
        If the answer isn't in the 'Context', say you lack the information and suggest the ODC website or direct contact.  AVOID hallucination or making up information.
        
        Example 1:
        Question: What is FabLab Solidaires?
        Answer: FabLab Solidaires is a free digital production workshop at Orange Digital Center, equipped with advanced tools like 3D printers and laser cutters. It supports young people and entrepreneurs in creating prototypes and turning their ideas into real-world products.

        Example 2:
        Question:  how to register
        Answer: To register for programs at Orange Digital Center, please visit www.orangedigitalcenters.com and complete the application form. You will be notified of the selection process by phone or email.

        Context: {context}
        Chat History: {chat_history}
        Question: {question}

        Answer:
        """
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="answer",
            return_messages=True,
            input_key="question",
            verbose=True
        )
        
        # Custom retriever with control over number of results (k)
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        
        self.rag_prompt = ChatPromptTemplate.from_template(rag_prompt_template)

        # RAG chain as a runnable sequence
        def load_memory_and_retrive(inputs: Dict[str, Any]):
            memory_variables = self.memory.load_memory_variables({})
            chat_history = memory_variables.get("chat_history", [])
            retrieved_docs = self.retriever.get_relevant_documents(inputs['question'])
            context = "\n".join([doc.page_content for doc in retrieved_docs])
            return {"context": context, "chat_history": chat_history, **inputs}
        
        self.rag_chain = (
            load_memory_and_retrive
            | self.rag_prompt
            | self.llm_rag
            | StrOutputParser()
        )
        
        general_prompt_template = """You are a friendly and professional AI Assistant.
        Your name is ODC AI Assistant. 
        You must ALWAYS respond in a helpful and professional tone.
        Be as brief as possible and avoid unnecessary details, remember it's a conversation so short and direct answers are preferred to keep a conversation.

        Guidelines:
        - Be direct and brief (5-7 sentences)
        - Try to minimize the number of words in the response and when there is more to say request if the user wants more details on that matter
        - Include relevant technical details only when asked.
        - Ignore irrelevant context from the chat history
        Chat History: {chat_history}
        Question: {question}

        Answer:"""
        
        self.general_memory = ConversationBufferMemory(
          memory_key="chat_history",
          output_key="answer",
          return_messages=True,
          input_key="question",
          verbose=True
        )

        self.general_prompt = PromptTemplate.from_template(general_prompt_template)
        # General LLM chain for questions not on the context of the fablab
        def load_general_memory(inputs: Dict[str, Any]):
              memory_variables = self.general_memory.load_memory_variables({})
              chat_history = memory_variables.get("chat_history", [])
              return {"chat_history": chat_history, **inputs}
        
        self.general_chain = (
            load_general_memory
            | self.general_prompt
            | self.llm_general
            | StrOutputParser()
        )

        self.clear_memory()  # Clear memory on initialization

        # classification prompt
        self.classification_prompt = """
        You are a classifier that analyzes a question and categorizes it into one of these three categories:
            - RAG_RELEVANT: The question is related to the Orange Digital Center and can be answered using the FabLab context.
            - GENERAL_KNOWLEDGE: The question is general and not related to the Orange Digital Center.
            - UNCLEAR: It is not clear if the question is related to the Orange Digital Center.

        The category MUST be one of the following: RAG_RELEVANT, GENERAL_KNOWLEDGE, or UNCLEAR. Output ONLY the category name.

        If you are not at least 80% confident in the classification, classify the question as UNCLEAR.

        Guidelines:
        - If the question's *intent* is clearly about specific programs, events, Trainings, registration, materials, support, or facilities at the Orange Digital Center, classify it as RAG_RELEVANT. The *intent* is more important than the exact wording.
        - If the question is about general knowledge or unrelated topics, classify it as GENERAL_KNOWLEDGE.
        - If the question is ambiguous or lacks enough context to determine its relevance, classify it as UNCLEAR.
        - Chat history is *crucial* for ambiguous questions. If the immediately preceding turn(s) of the conversation established the context as being about the Orange Digital Center, a specific program at ODC (e.g., FabLab), or a specific topic within ODC, then subsequent ambiguous questions (like "tell me more," "what else," "explain further") should be classified as RAG_RELEVANT.
        - If the chat history is empty or does not provide a clear context related to ODC, classify ambiguous questions as UNCLEAR.

        Examples:
        Question: "What programs does the Orange Digital Center offer?"
        Category: RAG_RELEVANT

        Question: "How do I learn to code?"
        Category: GENERAL_KNOWLEDGE

        Question: "Can you tell me more about the center?"
        Category: RAG_RELEVANT

        Question: "What is the meaning of life?"
        Category: GENERAL_KNOWLEDGE

        Question: "what is"
        Category: UNCLEAR

        Question: "Tell me about the FabLab"
        Category: RAG_RELEVANT

        Chat History: User: "What is the Orange Digital Center in Agadir?" Assistant: "..."
        Question: "Where is it located?"
        Category: RAG_RELEVANT

        Chat History: User: "I want to learn programming." Assistant: "..."
        Question: "What are some good languages to start with?"
        Category: GENERAL_KNOWLEDGE

        Chat History: User: "I want to develop a project at the fablab" Assistant: "Sure how can I assist you"
        Question: "what materials do you have ?"
        Category: RAG_RELEVANT

        Chat History: User: "Tell me about the fablab" Assistant: "The fablab offers ..."
        Question: "Tell me more"
        Category: RAG_RELEVANT

        Chat History:
        Question: "Tell me more"
        Category: UNCLEAR

        Chat History: User: "What is 3d printing ?";
        Question: "Tell me more";
        Category: GENERAL_KNOWLEDGE

        Question: {question}
        Category:
        """

        self.classification_chain = (
            PromptTemplate.from_template(self.classification_prompt)
            | self.llm_general
            | StrOutputParser()
        )
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
        if hasattr(self, 'general_memory'):
           self.general_memory.clear()

    def is_basic_chat(self, text):
        """Check if the input is a basic chat interaction"""
        text = text.lower().strip()
        return any(text in patterns for patterns in self.basic_chat_patterns.values())

    def get_basic_response(self, text, lang):
        """Handle basic chat interactions"""
        if lang == 'fr':
            return "Bonjour! Comment puis-je vous aider?"
        elif lang == 'ar':
            return "سلام! كيفاش نعاونك؟"
        else:
            return "Hello! How can I help you?"
    
    def classify_question(self, question):
        """Classifies the input question as RAG_RELEVANT, GENERAL_KNOWLEDGE or UNCLEAR"""
        try:
            memory_variables = self.memory.load_memory_variables({})
            chat_history = memory_variables.get("chat_history", [])
            classification = self.classification_chain.invoke({"question": question, "chat_history": chat_history})

            classification = classification.strip()  # Remove leading/trailing whitespace

            # Extract the category using regex (more robust)
            match = re.search(r"(RAG_RELEVANT|GENERAL_KNOWLEDGE|UNCLEAR)", classification)
            if match:
                classification = match.group(1)
            else:
                classification = "UNCLEAR"  # Default if parsing fails

            if classification not in ["RAG_RELEVANT", "GENERAL_KNOWLEDGE", "UNCLEAR"]:
                classification = "UNCLEAR"  # Default if parsing fails

            # Fuzzy Matching for Voice Command Issues - Optimized for Speed
            question_lower = question.lower()
            odc_keywords = ["orange", "digital", "center"]
            fablab_keywords = ["fablab", "fab lab"]

            if classification == "UNCLEAR":
                if any(fuzz.partial_ratio(keyword, question_lower) > 80 for keyword in odc_keywords):
                    classification = "RAG_RELEVANT"
                elif any(fuzz.partial_ratio(keyword, question_lower) > 80 for keyword in fablab_keywords):
                    classification = "RAG_RELEVANT"

            # Enhanced History Check:  Look back up to 2 turns
            if question.lower() in ["tell me more", "what else", "explain further"] and classification == "UNCLEAR":
                history_length = len(chat_history)
                if history_length >= 2:  # Check at least 2 turns back
                    last_turn = chat_history[-1]  # Last assistant turn
                    second_last_turn = chat_history[-2] # last user turn
                    if "orange digital center" in last_turn.content.lower() or "fablab" in last_turn.content.lower() or "odc" in last_turn.content.lower() or "orange" in last_turn.content.lower() or "digital" in last_turn.content.lower():
                       classification = "RAG_RELEVANT" # if the last turn of the assistant talked about fablab related or odc mark it as RAG_RELEVANT

            return classification
        except Exception as e:
            # Handle exception appropriately for your Kivy App
            print(f"Classification Error: {e}")  # Example
            return "UNCLEAR"

    def get_response(self, question, context=""):
        try:
            classification = self.classify_question(question)

            if classification == "RAG_RELEVANT":
                response = self.rag_chain.invoke({
                    "question": question,
                    "language": self.selected_language
                })
                # retriever = self.vector_store.as_retriever(search_kwargs={"k": 5}) #No Need To Have It Here
                retrieved_docs = self.retriever.get_relevant_documents(question)
                return {
                    "answer": response,
                    "sources": [doc.metadata.get('source', 'Unknown')
                            for doc in retrieved_docs]
                }
            elif classification == "GENERAL_KNOWLEDGE":
                response = self.general_chain.invoke({"question": question})
                return {"answer": response, "sources": []}
            else:
                # Use general LLM for fallback
                response = self.general_chain.invoke({"question": question})
                return {"answer": response, "sources": []}
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