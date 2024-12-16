import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from ..config import DATA_DIR, VECTOR_DB_PATH, CHUNK_SIZE, CHUNK_OVERLAP

class DocumentProcessor:
    def __init__(self):
        # Add batch processing
        self.batch_size = 32  # Adjust based on memory
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    
    def create_program_document(self):
        """Convert programs JSON to text format for embedding"""
        json_file = self.base_dir / "scraped_data.json"
        programs_txt = self.base_dir / "data" / "programs.txt"
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(programs_txt, 'w', encoding='utf-8') as f:
                f.write(f"{data['header']['title']}\n")
                f.write(f"{data['header']['subtitle']}\n\n")
                
                for program in data['programs']:
                    f.write(f"Program: {program['name']}\n")
                    f.write(f"Description: {program['description']}\n\n")
                    
                    f.write("Statistics:\n")
                    for stat in program['about_numbers']:
                        f.write(f"- {stat['title']}: {stat['value']}\n")
                        f.write(f"  {stat['description']}\n")
                    f.write("\n---\n\n")
                    
        except Exception as e:
            print(f"Error creating program document: {e}")

    def load_documents(self):
        loader = DirectoryLoader(
            DATA_DIR,
            glob="**/*.txt",
            loader_cls=TextLoader
        )
        documents = loader.load()
        return documents

    def process_documents(self):
        """Update to create program document before processing"""
        self.create_program_document()
        documents = self.load_documents()
        chunks = []
        
        # Process in batches
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            chunks.extend(self.text_splitter.split_documents(batch))
        
        # Create or load vector store
        vector_store = FAISS.from_documents(
            chunks,
            self.embeddings
        )
        
        # Save vector store
        vector_store.save_local(str(VECTOR_DB_PATH))
        return vector_store
    
    @staticmethod
    def load_vector_store():
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        return FAISS.load_local(str(VECTOR_DB_PATH), embeddings)
