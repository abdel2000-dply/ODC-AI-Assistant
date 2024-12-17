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
    print("Starting ODC event scheduler...")
    
    # Schedule multiple tasks if needed
    schedule.every().day.at("09:30").do(update_events)  # Daily event updates
    # Add any other scheduled tasks from scheduler.py here
    
    # Initial run
    update_events()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
