from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

@dataclass
class Event:
    title: str
    start_date: str
    end_date: str
    location: str
    month: str
    day: str

def test_scrape_events():
    url = "https://www.orangedigitalcenters.com/country/ma/events"
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    
    try:
        print("Initializing browser...")
        driver = webdriver.Chrome(options=chrome_options)
        print("Fetching events...")
        driver.get(url)
        
        # Wait for events to load
        time.sleep(5)  # Give React time to render
        
        # Find all event divs
        event_divs = driver.find_elements(By.CLASS_NAME, "event-detail")
        events = []
        
        for event_div in event_divs:
            try:
                month = event_div.find_element(By.CLASS_NAME, "alphabetic-month").text.strip()
                day = event_div.find_element(By.CLASS_NAME, "numeric-date").text.strip()
                title = event_div.find_element(By.CLASS_NAME, "event-title").text.strip()
                
                dates = event_div.find_elements(By.CLASS_NAME, "from-to-date-wrapper")
                dates = [d.find_element(By.TAG_NAME, "p").text.strip() for d in dates]
                
                start_date = dates[0] if dates else "N/A"
                end_date = dates[1] if len(dates) > 1 else "N/A"
                location = 'ODC Agadir' if 'Agadir' in title else 'ODC Other'
                
                event = Event(
                    title=title,
                    start_date=start_date,
                    end_date=end_date,
                    location=location,
                    month=month,
                    day=day
                )
                events.append(event)
                
            except Exception as e:
                print(f"Error parsing event: {e}")
                continue
        
        # Print events
        print("\nUpcoming Events at Orange Digital Center:")
        print("=" * 50)
        for event in events:
            print(f"\nEvent: {event.title}")
            print(f"Date: {event.month} {event.day}")
            print(f"From: {event.start_date}")
            print(f"To: {event.end_date}")
            print(f"Location: {event.location}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error fetching events: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_scrape_events()
