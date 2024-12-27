from src.utils.document_processor import DocumentProcessor

def test_vector_store():
    # Load the vector store
    vector_store = DocumentProcessor.load_vector_store()
    
    # First, show all available documents
    print("Available Documents in Vector Store:")
    print("-" * 50)
    try:
        all_docs = vector_store.similarity_search("", k=10)
        print(f"Total documents found: {len(all_docs)}")
        for i, doc in enumerate(all_docs, 1):
            print(f"\nDocument {i}:")
            print(f"Source: {doc.metadata.get('source', 'N/A')}")
            print(f"First 100 chars: {doc.page_content[:100]}...")
    except Exception as e:
        print(f"Error retrieving documents: {e}")

    # Test specific queries
    test_queries = [
        "What is Orange Digital Center?",
        "What programs does ODC offer?",
        "Tell me about the Coding School at ODC",
        "What is FabLab?",
        "How does ODC help startups?",
        "Upcoming trainings",
        "formation"
    ]
    
    print("\n\nTesting Specific Queries:")
    print("-" * 50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 30)
        docs = vector_store.similarity_search(query, k=2)
        for i, doc in enumerate(docs, 1):
            print(f"\nResult {i}:")
            print(f"Content: {doc.page_content[:200]}...")
            print(f"Source: {doc.metadata.get('source', 'N/A')}")
            print(f"Similarity Score: {getattr(doc, 'score', 'N/A')}")

if __name__ == "__main__":
    test_vector_store()
