from pathlib import Path
from src.utils.event_scraper import EventScraper
from src.utils.document_processor import DocumentProcessor

def setup_assistant():
    print("Setting up ODC Assistant...")
    
    # 1. Ensure data directory exists
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    # 2. Scrape latest events
    print("\nScraping latest events...")
    scraper = EventScraper()
    scraper.scrape_events()
    
    # 3. Process all documents
    print("\nProcessing documents and creating embeddings...")
    processor = DocumentProcessor()
    vector_store = processor.process_documents()
    
    print("\nSetup complete! You can now run: python src/main.py")

if __name__ == "__main__":
    setup_assistant()
