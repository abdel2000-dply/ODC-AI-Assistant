from src.utils.document_processor import DocumentProcessor

def main():
    print("Starting document processing...")
    processor = DocumentProcessor()
    vector_store = processor.process_documents()
    print("Documents processed and vector store created successfully!")
    print(f"Vector store saved to: {processor.vector_store_path}")

if __name__ == "__main__":
    main()
