from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
import time

# Load single text file
print("Loading document...")
loader = TextLoader("./careerdev.txt")
documents = loader.load()

# Split documents into chunks
print("Splitting text into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
)
chunks = text_splitter.split_documents(documents)
print(f"Created {len(chunks)} chunks")

# Embed chunks
print("Loading embedding model (lightweight version for edge devices)...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create and save FAISS index
print("Creating FAISS index...")
db = FAISS.from_documents(chunks, embeddings)
print("Index created successfully!")

# Save the index
print("Saving index to disk...")
db.save_local("faiss_index")
print("Index saved to ./faiss_index/")

# Test query
query = "What is global branding?"
print(f"\nSearching for: '{query}'")
docs = db.similarity_search(query, k=2)

# Display results
print("\nResults:")
for i, doc in enumerate(docs, 1):
    print(f"\nResult {i}:")
    print("=" * 50)
    print(doc.page_content)
    print("=" * 50)

# Later you can load it back
# db = FAISS.load_local("faiss_index", embeddings)
