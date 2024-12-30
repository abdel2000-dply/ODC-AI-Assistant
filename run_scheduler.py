import schedule
import time
from datetime import datetime, timedelta
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

def check_and_run_missed_update():
    now = datetime.now()
    last_monday = now - timedelta(days=now.weekday())
    scheduled_time = last_monday.replace(hour=9, minute=30, second=0, microsecond=0)
    
    if now > scheduled_time and (now - scheduled_time).days < 7:
        print("Missed scheduled update, running now...")
        update_events()

def main():
    print("Starting ODC event scheduler...")
    
    # Schedule the update to run every Monday at 9:30 AM
    schedule.every().monday.at("09:30").do(update_events)
    
    # Check and run missed update if necessary
    check_and_run_missed_update()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
