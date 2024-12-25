from langchain_cohere import ChatCohere
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain.schema import Document
from typing import List, Dict, Optional
import logging
from datetime import datetime
from src.utils.document_processor import DocumentProcessor
import os
from dotenv import load_dotenv
from langdetect import detect

class EnhancedLangChainHandler:
    SUPPORTED_LANGUAGES = {
        '1': {'code': 'en', 'name': 'English'},
        '2': {'code': 'fr', 'name': 'French'},
        '3': {'code': 'ar', 'name': 'Arabic/Darija'}
    }

    def __init__(
        self,
        selected_language: str = 'en',
        model_name: str = "command-r-plus-08-2024",
        temperature: float = 0.3,
        memory_window: int = 5,
        max_tokens: int = 300
    ):
        load_dotenv()
        self._setup_logging()
        self._initialize_llm(model_name, temperature, max_tokens)
        self._setup_retriever()
        self._setup_memory(memory_window)
        self._setup_chain()
        self.selected_language = selected_language

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='assistant_logs.log'
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_llm(self, model_name: str, temperature: float, max_tokens: int):
        try:
            self.llm = ChatCohere(
                cohere_api_key=os.getenv('COHERE_API_KEY'),
                temperature=temperature,
                max_tokens=max_tokens,
                model=model_name,
                callbacks=[StreamingStdOutCallbackHandler()]
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM: {str(e)}")
            raise

    def _setup_retriever(self):
        try:
            base_retriever = DocumentProcessor.load_vector_store().as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={
                    "k": 3,
                    "score_threshold": 0.7,
                    "fetch_k": 5
                }
            )
            
            self.retriever = TimeWeightedVectorStoreRetriever(
                vectorstore=base_retriever.vectorstore,
                decay_rate=0.95,
                k=3
            )
        except Exception as e:
            self.logger.error(f"Failed to setup retriever: {str(e)}")
            raise

    def _setup_memory(self, window_size: int):
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            output_key="answer",
            return_messages=True,
            input_key="question",
            k=window_size
        )

    def _setup_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional AI Assistant for Fablab Orange digital center.
            Response Language: {language}
            Tone: Professional and concise
            Context: {context}
            
            Guidelines:
            - Respond ONLY in the specified language
            - Be direct and brief
            - Provide specific examples when relevant
            - If unsure, acknowledge limitations
            - Include relevant technical details only when asked"""),
            ("human", "{question}"),
            ("assistant", "Let me help you with that.")
        ])

        try:
            self.chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.retriever,
                memory=self.memory,
                combine_docs_chain_kwargs={"prompt": prompt},
                return_source_documents=True,
                verbose=True
            )
        except Exception as e:
            self.logger.error(f"Failed to setup chain: {str(e)}")
            raise

    async def get_response_async(
        self,
        question: str,
        context: Optional[str] = ""
    ) -> Dict:
        try:
            self.logger.info(f"Processing question: {question[:100]}...")
            
            response = await self.chain.ainvoke({
                "question": question,
                "language": self.selected_language
            })
            
            sources = response.get("source_documents", [])
            
            # Log retrieval metrics
            self.logger.info(f"Retrieved {len(sources)} documents with scores: " + 
                           ", ".join([f"{doc.metadata.get('score', 'N/A')}" for doc in sources]))
            
            return {
                "answer": response.get("answer", "No answer generated"),
                "sources": [self._format_source(doc) for doc in sources],
                "confidence": self._calculate_confidence(sources)
            }
            
        except Exception as e:
            self.logger.error(f"Error in get_response: {str(e)}")
            return self._get_error_response()

    def _format_source(self, doc: Document) -> Dict:
        return {
            "source": doc.metadata.get('source', 'Unknown'),
            "score": doc.metadata.get('score', 0),
            "timestamp": doc.metadata.get('timestamp', datetime.now().isoformat())
        }

    def _calculate_confidence(self, sources: List[Document]) -> float:
        if not sources:
            return 0.0
        scores = [doc.metadata.get('score', 0) for doc in sources]
        return sum(scores) / len(scores) if scores else 0.0

    def _get_error_response(self) -> Dict:
        error_messages = {
            'en': "I apologize, but I encountered an error processing your request.",
            'fr': "Je suis désolé, mais j'ai rencontré une erreur lors du traitement de votre demande.",
            'ar': "عذراً، واجهت مشكلة في معالجة طلبك."
        }
        return {
            "answer": error_messages.get(self.selected_language, error_messages['en']),
            "sources": [],
            "confidence": 0.0
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

if __name__ == "__main__":
    # Get language preference at startup
    selected_language = EnhancedLangChainHandler.select_language()
    handler = EnhancedLangChainHandler(selected_language)
    
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
                
            response = handler.get_response_async(user_input)
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
