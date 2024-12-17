from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

print("Loading embedding model...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print("Loading FAISS index...")
db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

# Test different queries
# query = "What are the drawbacks of global branding?"  # or
# query = "What are some strategies for global branding?"
query = "How to implement global branding?"

print(f"\nSearching for: '{query}'")
docs = db.similarity_search(query, k=3)

# Display results
print("\nResults:")
for i, doc in enumerate(docs, 1):
    print(f"\nResult {i}:")
    print("=" * 50)
    print(doc.page_content)
    print("=" * 50)