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

class EventScraper:
    def __init__(self):
        self.url = "https://www.orangedigitalcenters.com/country/ma/events"
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.is_raspberry_pi = platform.machine().startswith('arm') or platform.machine().startswith('aarch')
        self.service = Service('/usr/bin/chromedriver') if self.is_raspberry_pi else Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.driver.maximize_window()
        self.initial_url = self.driver.current_url

    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present and return it"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))

    def wait_for_detail_page(self, timeout=10):
        """Wait for event detail page to load"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "odc-country-detail-event-header"))
            )
            return True
        except:
            return False

    def get_event_list(self):
        """Get fresh list of events"""
        section = self.wait_for_element(By.XPATH, "//div[h5[contains(text(), 'Évènements à venir')]]")
        return section.find_elements(By.CLASS_NAME, "event-detail")

    def get_clean_description(self):
        """Extract and clean description text with better selector"""
        try:
            # Wait for content section to be present
            content_div = self.wait_for_element(By.CSS_SELECTOR, ".content2 > div:nth-child(2)")
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

    def scrape_events(self):
        try:
            print("Initializing browser...")
            self.driver.get(self.url)

            # Wait for events to load
            time.sleep(5)  # Give React time to render

            # Get initial event count
            event_divs = self.get_event_list()
            total_events = len(event_divs)
            print(f"Found {total_events} upcoming events")
            events = []

            # Process each event by index
            for index in range(total_events):
                try:
                    # Get fresh list and current event
                    event_divs = self.get_event_list()
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
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", current_event)
                    time.sleep(2)
                    
                    # Try multiple click methods
                    try:
                        current_event.click()
                    except:
                        try:
                            self.driver.execute_script("arguments[0].click();", current_event)
                        except:
                            print(f"Failed to click event: {title}")
                            continue

                    # Wait for detail page to load
                    if not self.wait_for_detail_page():
                        print(f"Failed to load details for: {title}")
                        self.driver.get(self.initial_url)
                        time.sleep(3)
                        continue

                    # Get event details with explicit waits
                    try:
                        header = self.wait_for_element(By.CLASS_NAME, "odc-country-detail-event-header")
                        time_elements = self.wait_for_element(By.CLASS_NAME, "date-time-wrapper").find_elements(By.CLASS_NAME, "wrapper-date-time")
                        location = self.wait_for_element(By.CSS_SELECTOR, ".wrapper-location2 span").text.strip()
                        
                        if 'Agadir' in location:
                            # Get description with improved extraction
                            description = self.get_clean_description()
                            
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
                        self.driver.get(self.initial_url)
                        time.sleep(3)
                
                except Exception as e:
                    print(f"Error processing event {index + 1}: {e}")
                    self.driver.get(self.initial_url)
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
            self.driver.quit()

def test_scrape_events():
    scraper = EventScraper()
    scraper.scrape_events()

if __name__ == "__main__":
    test_scrape_events()