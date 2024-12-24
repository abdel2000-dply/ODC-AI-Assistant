import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

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
    events = scraper.scrape_events()
    
    if not events:
        print("Note: Using default events content")
    else:
        print(f"Successfully scraped {len(events)} events")
    
    # 3. Process all documents and create vector store
    print("\n2. Processing all documents...")
    processor = DocumentProcessor()
    vector_store = processor.process_documents()
    
    if vector_store:
        print("\nSetup completed successfully!")
        print(f"Data directory contains: {', '.join(f.name for f in data_dir.glob('*'))}")
        print("\nYou can now run:")
        print("1. python run_scheduler.py (in one terminal)")
        print("2. python src/main.py (in another terminal)")
    else:
        print("\nSetup completed with warnings. Please check the logs above.")

if __name__ == "__main__":
    setup_assistant()
