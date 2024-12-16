from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_PATH = DATA_DIR / "vectorstore"

# Vector DB settings
# Reduce these values for Pi
CHUNK_SIZE = 250  # Smaller chunks
CHUNK_OVERLAP = 25  # Less overlap

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
VECTOR_DB_PATH.mkdir(exist_ok=True)
