import schedule
import time
from utils.event_manager import EventManager

def update_job():
    """Run the event update job"""
    manager = EventManager()
    manager.update_events()

def run_scheduler():
    """Setup and run the scheduler"""
    print("Starting scheduler...")
    
    # Schedule updates every Monday at 8:00 AM
    schedule.every().monday.at("08:00").do(update_job)
    
    # Run immediately on start
    update_job()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()
