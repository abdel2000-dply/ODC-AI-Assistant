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
    
    def wait_for_element(driver, by, value, timeout=10):
        """Wait for an element to be present and return it"""
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))

    def wait_for_detail_page(driver, timeout=10):
        """Wait for event detail page to load"""
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "odc-country-detail-event-header"))
            )
            return True
        except:
            return False

    def get_event_list():
        """Get fresh list of events"""
        section = wait_for_element(driver, By.XPATH, "//div[h5[contains(text(), 'Évènements à venir')]]")
        return section.find_elements(By.CLASS_NAME, "event-detail")

    def get_clean_description(driver):
        """Extract and clean description text with better selector"""
        try:
            # Wait for content section to be present
            content_div = wait_for_element(driver, By.CSS_SELECTOR, ".content2 > div:nth-child(2)")
            # Get all paragraphs except the last one (which usually contains hashtags)
            paragraphs = content_div.find_elements(By.TAG_NAME, "p")
            # Filter and join paragraphs
            description = "\n".join([
                p.text.strip() for p in paragraphs 
                if p.text.strip() and not any(tag in p.text for tag in ['#', 'Orange', 'ODC'])
            ])
            return description
        except Exception as e:
            print(f"Error extracting description: {e}")
            return ""

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

        # Get initial event count
        event_divs = get_event_list()
        total_events = len(event_divs)
        print(f"Found {total_events} upcoming events")
        events = []
        initial_url = driver.current_url

        # Process each event by index
        for index in range(total_events):
            try:
                # Get fresh list and current event
                event_divs = get_event_list()
                if index >= len(event_divs):
                    print(f"Event index {index} out of range")
                    continue

                current_event = event_divs[index]
                
                # Get basic info
                title = current_event.find_element(By.CLASS_NAME, "event-title").text.strip()
                month = current_event.find_element(By.CLASS_NAME, "alphabetic-month").text.strip()
                day = current_event.find_element(By.CLASS_NAME, "numeric-date").text.strip()
                
                print(f"\nProcessing {index + 1}/{total_events}: {title}")
                
                # Scroll and click with better handling
                driver.execute_script("arguments[0].scrollIntoView(true);", current_event)
                time.sleep(2)
                
                # Try multiple click methods
                try:
                    current_event.click()
                except:
                    try:
                        driver.execute_script("arguments[0].click();", current_event)
                    except:
                        print(f"Failed to click event: {title}")
                        continue

                # Wait for detail page to load
                if not wait_for_detail_page(driver):
                    print(f"Failed to load details for: {title}")
                    driver.get(initial_url)
                    time.sleep(3)
                    continue

                # Get event details with explicit waits
                try:
                    header = wait_for_element(driver, By.CLASS_NAME, "odc-country-detail-event-header")
                    time_elements = wait_for_element(driver, By.CLASS_NAME, "date-time-wrapper").find_elements(By.CLASS_NAME, "wrapper-date-time")
                    location = wait_for_element(driver, By.CSS_SELECTOR, ".wrapper-location2 span").text.strip()
                    
                    if 'Agadir' in location:
                        # Get description with improved extraction
                        description = get_clean_description(driver)
                        
                        events.append(Event(
                            title=title,
                            start_date=time_elements[0].text if time_elements else "N/A",
                            end_date=time_elements[1].text if len(time_elements) > 1 else "N/A",
                            location=location,
                            month=month,
                            day=day,
                            description=description
                        ))
                        print(f"Added Agadir event: {title}")
                        print(f"Description found: {bool(description)}")
                
                finally:
                    # Always return to main page
                    driver.get(initial_url)
                    time.sleep(3)
            
            except Exception as e:
                print(f"Error processing event {index + 1}: {e}")
                driver.get(initial_url)
                time.sleep(3)

        # Print events with better formatting
        print("\nUpcoming Events at Orange Digital Center Agadir:")
        print("=" * 50)
        for event in events:
            print(f"\nEvent: {event.title}")
            print(f"Date: {event.month} {event.day}")
            print(f"Start: {event.start_date}")
            print(f"End: {event.end_date}")
            print(f"Location: {event.location}")
            if event.description:
                print("\nDescription:")
                for line in event.description.split('\n'):
                    print(f"  {line}")
            print("-" * 50)

    except Exception as e:
        print(f"Error fetching events: {e}")
    finally:
        driver.quit()

# if __name__ == "__main__":
#     # Add retry mechanism for Raspberry Pi
#     max_retries = 3
#     for attempt in range(max_retries):
#         try:
#             test_scrape_events()
#             break
#         except Exception as e:
#             print(f"Attempt {attempt + 1} failed: {e}")
#             if attempt < max_retries - 1:
#                 print("Retrying in 10 seconds...")
#                 time.sleep(10)
#             else:
#                 print("All attempts failed")

from src.utils.event_scraper import EventScraper

def main():
    scraper = EventScraper()
    print("Starting event scraping...")
    
    events = scraper.scrape_events()
    
    print("\nScraped Events Summary:")
    print(f"Total events found: {len(events)}")
    
    for i, event in enumerate(events, 1):
        print(f"\nEvent {i}:")
        for key, value in event.items():
            print(f"{key}: {value}")
        print("-" * 50)

if __name__ == "__main__":
    main()
