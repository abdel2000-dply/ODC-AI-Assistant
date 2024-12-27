from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from pathlib import Path
from ..config import DATA_DIR, VECTOR_DB_PATH, CHUNK_SIZE, CHUNK_OVERLAP

class DocumentProcessor:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.vector_store_path = VECTOR_DB_PATH
        
        # Use the tested configurations
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,  # Use updated config value
            chunk_overlap=CHUNK_OVERLAP,  # Use updated config value
            length_function=len,
        )
        
        # Use the lightweight model we tested
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    
    def load_documents(self):
        """Load all .txt files from data directory"""
        print("Loading documents from data directory...")
        loader = DirectoryLoader(
            str(self.data_dir),
            glob="*.txt",  # Only process root txt files
            loader_cls=TextLoader
        )
        return loader.load()

    def process_documents(self):
        """Process documents and create vector store"""
        try:
            # Load and split documents
            print("Processing documents...")
            documents = self.load_documents()
            print(f"Found {len(documents)} documents")
            
            print("Splitting into chunks...")
            chunks = self.text_splitter.split_documents(documents)
            print(f"Created {len(chunks)} chunks")
            
            # Create vector store
            print("Creating FAISS index...")
            vector_store = FAISS.from_documents(chunks, self.embeddings)
            
            # Save vector store
            print("Saving index to disk...")
            vector_store.save_local(str(self.vector_store_path))
            print(f"Index saved to {self.vector_store_path}")
            
            return vector_store
            
        except Exception as e:
            print(f"Error processing documents: {e}")
            return None
    
    @staticmethod
    def load_vector_store():
        """Load existing vector store with the lightweight model"""
        try:
            print("Loading FAISS index...")
            if not VECTOR_DB_PATH.exists():
                print("Vector store not found. Please run setup.py first")
                return None
                
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            return FAISS.load_local(str(VECTOR_DB_PATH), embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
            print(f"Error loading vector store: {e}")
            print("Please ensure setup.py has been run to initialize the vector store")
            return None
