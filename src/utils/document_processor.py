import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from pathlib import Path
from ..config import DATA_DIR, VECTOR_DB_PATH, CHUNK_SIZE, CHUNK_OVERLAP
from langchain.schema import Document

class JSONLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Extract content based on known keys and place it into the 'content' field
            if 'fablab_materials' in data:
                content = data['fablab_materials']
            elif 'knowledge_base' in data:
                content = data['knowledge_base']
            elif 'message' in data:
                content = data['message']
            else:
                content = data.get('content', '')
            return Document(page_content=str(content), metadata={"source": str(self.file_path)})

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
        """Load all .json files from data directory"""
        print("Loading documents from data directory...")
        documents = []
        for json_file in self.data_dir.glob("*.json"):
            loader = JSONLoader(json_file)
            document = loader.load()
            if document.page_content:
                documents.append(document)
            else:
                print(f"No content found in {json_file}")
        print(f"Loaded {len(documents)} documents")
        return documents

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

    def retrieve_context(self, query):
        """Retrieve context based on the query"""
        try:
            print("Loading FAISS index...")
            vector_store = self.load_vector_store()
            if vector_store is None:
                print("Vector store not found. Please run setup.py first")
                return None

            print("Generating query embedding...")
            query_embedding = self.embeddings.embed_query(query)

            print("Using retriever to search for similar chunks...")
            retriever = vector_store.as_retriever()
            similar_chunks = retriever.retrieve(query_embedding, k=5)  # Retrieve top 5 similar chunks

            print("Retrieved context:")
            for chunk in similar_chunks:
                print(chunk.page_content)
            
            return similar_chunks
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return None
