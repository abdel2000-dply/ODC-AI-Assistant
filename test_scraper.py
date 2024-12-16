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
        
        def get_event_details(driver, event_div):
            """Get detailed information for an event"""
            initial_url = driver.current_url
            try:
                # Click event
                driver.execute_script("arguments[0].click();", event_div)
                time.sleep(2)

                # Wait for detail page
                detail_header = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "odc-country-detail-event-header"))
                )

                # Get dates
                dates = detail_header.find_elements(By.CLASS_NAME, "wrapper-date-time")
                start_date = dates[0].text if dates else "N/A"
                end_date = dates[1].text if len(dates) > 1 else "N/A"

                # Get venue
                venue = detail_header.find_element(By.CLASS_NAME, "wrapper-location2").find_element(By.TAG_NAME, "span").text.strip()

                # Get description
                description = []
                try:
                    content_div = driver.find_element(By.CSS_SELECTOR, ".content2 div:not(.ant-row)")
                    paragraphs = content_div.find_elements(By.TAG_NAME, "p")
                    for p in paragraphs:
                        text = p.text.strip()
                        if text and not text.startswith('#'):
                            description.append(text)
                except Exception as e:
                    print(f"Error getting description: {e}")

                return start_date, end_date, venue, '\n'.join(description)
            finally:
                driver.get(initial_url)
                time.sleep(2)

        events = []
        for event_div in event_divs:
            try:
                # Get basic info
                month = event_div.find_element(By.CLASS_NAME, "alphabetic-month").text.strip()
                day = event_div.find_element(By.CLASS_NAME, "numeric-date").text.strip()
                title = event_div.find_element(By.CLASS_NAME, "event-title").text.strip()

                # Check if it's an Agadir event
                if 'Agadir' in title:
                    # Get detailed info
                    start_date, end_date, venue, description = get_event_details(driver, event_div)
                    
                    event = Event(
                        title=title,
                        start_date=start_date,
                        end_date=end_date,
                        location='ODC Agadir',
                        month=month,
                        day=day,
                        description=description,
                        venue=venue
                    )
                    events.append(event)
                
            except Exception as e:
                print(f"Error parsing event: {e}")
                continue

        # Print events with enhanced formatting
        print("\nUpcoming Events at Orange Digital Center Agadir:")
        print("=" * 50)
        for event in events:
            print(f"\nEvent: {event.title}")
            print(f"Date: {event.month} {event.day}")
            print(f"From: {event.start_date}")
            print(f"To: {event.end_date}")
            print(f"Venue: {event.venue}")
            if event.description:
                print("\nDescription:")
                for line in event.description.split('\n'):
                    print(f"  {line}")
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
