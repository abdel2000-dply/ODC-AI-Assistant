from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_PATH = DATA_DIR / "vectorstore"

# Vector DB settings
# Reduce these values for Pi
CHUNK_SIZE = 500  # Increased chunk size
CHUNK_OVERLAP = 50  # Increased overlap

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
VECTOR_DB_PATH.mkdir(exist_ok=True)
