from pathlib import Path
from src.utils.event_scraper import EventScraper
from src.utils.document_processor import DocumentProcessor

def setup_assistant():
    print("Setting up ODC Assistant...")
    
    # 1. Ensure data directory exists
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    # 2. Scrape latest events
    print("\n1. Scraping latest events...")
    scraper = EventScraper()
    scraper.scrape_events()
    print("Events saved to data/events.txt")
    
    # 3. Process all documents and create vector store
    print("\n2. Processing all documents (including events)...")
    processor = DocumentProcessor()
    vector_store = processor.process_documents()
    print(f"Vector store created at {processor.vector_store_path}")
    
    print("\nSetup complete! You can now run:")
    print("1. python run_scheduler.py (in one terminal)")
    print("2. python src/main.py (in another terminal)")

if __name__ == "__main__":
    setup_assistant()
