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
from pathlib import Path
import json

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
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.events_file = self.data_dir / "upcoming_training_events.json"
        self.data_dir.mkdir(exist_ok=True)

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

    def _save_events(self, events):
        """Save events to JSON file"""
        print(f"Saving events to {self.events_file}")
        events_data = {
            "content": [{
                "info": "This is a list of upcoming trainings/events/formation in ODC Agadir",
                "title": event.title,
                "start_date": event.start_date,
                "end_date": event.end_date,
                "location": event.location,
                "month": event.month,
                "day": event.day,
                "description": event.description,
                "venue": event.venue
            } for event in events]
        }
        
        with open(self.events_file, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, ensure_ascii=False, indent=4)
        
        print(f"Events saved to {self.events_file}")

    def _save_default_content(self):
        """Save default content when scraping fails"""
        print("Saving default content...")     
        default_content = {
            "content": "I'm sorry I couldn't access that information now due to some technical issues. Please ask a manager or visit https://www.orangedigitalcenters.com/country/ma/events for the latest events."
        }
        with open(self.events_file, 'w', encoding='utf-8') as f:
            json.dump(default_content, f, ensure_ascii=False, indent=4)
        print(f"Default content saved to {self.events_file}")

    def scrape_events(self):
        events = []
        try:
            print("Initializing browser...")
            self.chrome_options = Options()
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            self.chrome_options.add_argument("--ignore-certificate-errors")
            self.is_raspberry_pi = platform.machine().startswith('arm') or platform.machine().startswith('aarch')
            self.service = Service('/usr/bin/chromedriver') if self.is_raspberry_pi else Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            self.driver.maximize_window()
            self.driver.get(self.url)
            self.initial_url = self.driver.current_url

            # Wait for events to load
            time.sleep(7)  # Give React time to render

            # Get initial event count
            event_divs = self.get_event_list()
            total_events = len(event_divs)
            print(f"Found {total_events} upcoming events")

            # Process each event by index
            for index in range(total_events):
                try:
                    # Refresh the event list before processing each event
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
                    time.sleep(4)
                    
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
                        time.sleep(5)
                
                except Exception as e:
                    print(f"Error processing event {index + 1}: {e}")
                    self.driver.get(self.initial_url)
                    time.sleep(3)

            # After successfully scraping events and before printing them:
            if events:
                self._save_events(events)  # Save events before returning
                print(f"Successfully saved {len(events)} events")
            else:
                print("No events could be scraped")
                self._save_default_content()

            return events

        except Exception as e:
            print(f"Error fetching events: {e}")
            self._save_default_content()
            return []
        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()

def test_scrape_events():
    scraper = EventScraper()
    scraper.scrape_events()

if __name__ == "__main__":
    test_scrape_events()