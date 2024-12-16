from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import platform
import subprocess

@dataclass
class Event:
    title: str
    start_date: str
    end_date: str
    location: str
    month: str
    day: str
    description: str = ""  # Added description field
    venue: str = ""        # Added venue field

def test_scrape_events():
    url = "https://www.orangedigitalcenters.com/country/ma/events"
    
    # Configure Chrome options for Raspberry Pi
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    
    try:
        print("Initializing browser...")
        # Check if running on Raspberry Pi
        is_raspberry_pi = platform.machine().startswith('arm') or platform.machine().startswith('aarch')
        
        if is_raspberry_pi:
            service = Service('/usr/bin/chromedriver')
        else:
            service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.maximize_window()
        print("Fetching events...")
        driver.get(url)

        # Wait for events to load
        time.sleep(5)  # Give React time to render

        # Find upcoming events section specifically
        upcoming_section = driver.find_element(By.XPATH, "//div[h5[contains(text(), 'Évènements à venir')]]")
        
        # Find event divs within upcoming section
        event_divs = upcoming_section.find_elements(By.CLASS_NAME, "event-detail")
        print(f"Found {len(event_divs)} upcoming events")
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
        print("\nUpcoming Events at Orange Digital Center Agadir:")
        print("=" * 50)
        for event in events:
            if event.location == 'ODC Agadir':
                print(f"\nEvent: {event.title}")
                print(f"Date: {event.month} {event.day}")
                print(f"From: {event.start_date}")
                print(f"To: {event.end_date}")
                print(f"Location: {event.location}")
                print("-" * 50)

    except Exception as e:
        print(f"Error fetching events: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Add retry mechanism for Raspberry Pi
    max_retries = 3
    for attempt in range(max_retries):
        try:
            test_scrape_events()
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("Retrying in 10 seconds...")
                time.sleep(10)
            else:
                print("All attempts failed")
