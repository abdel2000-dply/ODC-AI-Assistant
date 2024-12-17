import schedule
import time
from src.utils.event_scraper import EventScraper
from src.utils.document_processor import DocumentProcessor

def update_events():
    print("Scheduled update: Scraping events...")
    scraper = EventScraper()
    scraper.scrape_events()
    
    print("Processing updated documents...")
    processor = DocumentProcessor()
    processor.process_documents()
    
    print("Update complete!")

def main():
    print("Starting event scheduler...")
    
    # Schedule event updates
    schedule.every().day.at("00:00").do(update_events)  # Run daily at midnight
    # For testing: schedule.every(1).minutes.do(update_events)
    
    # Initial run
    update_events()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
