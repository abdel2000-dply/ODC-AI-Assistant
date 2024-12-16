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
            # Install chromium-chromedriver if not present
            try:
                subprocess.run(['which', 'chromedriver'], check=True)
            except subprocess.CalledProcessError:
                print("Installing chromedriver...")
                subprocess.run(['sudo', 'apt-get', 'update'], check=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'chromium-chromedriver'], check=True)
            
            # Use system chromedriver on Raspberry Pi
            service = Service('/usr/bin/chromedriver')
        else:
            # Use ChromeDriverManager on other systems
            service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        wait = WebDriverWait(driver, 10)
        driver.maximize_window()  # Maximize to ensure elements are clickable
        print("Fetching events...")
        driver.get(url)
        
        # Wait for events to load and get fresh elements
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "past-future-events")))
        time.sleep(3)
        
        # Get all event rows with retry mechanism
        def get_event_elements():
            try:
                upcoming_section = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "past-future-events"))
                )
                event_rows = upcoming_section.find_elements(By.CLASS_NAME, "ant-row.event-detail")
                count = len(event_rows)
                if count == 0:
                    print("Warning: No events found, waiting 5 seconds and retrying...")
                    time.sleep(5)
                    event_rows = upcoming_section.find_elements(By.CLASS_NAME, "ant-row.event-detail")
                    count = len(event_rows)
                print(f"Found {count} events")
                return event_rows
            except Exception as e:
                print(f"Error getting events: {e}")
                return []

        def clean_description(description_text):
            """Clean and format the description text"""
            if not description_text:
                return ""
            # Remove the "Réserver une place" button text if present
            lines = [line.strip() for line in description_text.split('\n') if line.strip()]
            # Filter out lines that are just hashtags
            lines = [line for line in lines if not line.strip().startswith('#')]
            return '\n'.join(lines)

        def get_location_from_detail(detail_content, wait):
            """Extract location from detail page"""
            try:
                location_span = detail_content.find_element(By.CLASS_NAME, "wrapper-location2").find_element(By.TAG_NAME, "span")
                return location_span.text.strip()
            except Exception as e:
                print(f"Error getting location: {e}")
                return ""

        # Memory optimization for Raspberry Pi
        def process_events():
            events = []
            initial_url = driver.current_url
            
            while True:
                try:
                    # Get fresh list of events
                    event_divs = get_event_elements()
                    if not event_divs:
                        print("No events to process")
                        break

                    # Process only unprocessed events
                    processed_count = len(events)
                    if processed_count >= len(event_divs):
                        break

                    current_event = event_divs[processed_count]
                    
                    try:
                        # Extract info before clicking
                        title = current_event.find_element(By.CLASS_NAME, "event-title").text.strip()
                        month = current_event.find_element(By.CLASS_NAME, "alphabetic-month").text.strip()
                        day = current_event.find_element(By.CLASS_NAME, "numeric-date").text.strip()
                        
                        print(f"\nProcessing event {processed_count + 1}/{len(event_divs)}: {title}")
                        
                        # Click event
                        try:
                            current_event.click()
                        except:
                            driver.execute_script("arguments[0].click();", current_event)

                        # Wait for page load
                        wait.until(lambda d: d.current_url != initial_url)
                        
                        # Get event details
                        detail_content = wait.until(
                            EC.presence_of_element_located((By.CLASS_NAME, "odc-country-detail-event-header"))
                        )
                        
                        location = get_location_from_detail(detail_content, wait)
                        print(f"Found location: {location}")
                        
                        if 'Agadir' in location:
                            print("Found Agadir event! Processing details...")
                            
                            # Get dates
                            dates = detail_content.find_elements(By.CLASS_NAME, "wrapper-date-time")
                            start_date = dates[0].text if dates else "N/A"
                            end_date = dates[1].text if len(dates) > 1 else "N/A"
                            
                            # Get description
                            description = ""
                            try:
                                description_div = wait.until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, ".content2 div:not(.ant-row)"))
                                )
                                description = clean_description('\n'.join(
                                    p.text.strip() for p in description_div.find_elements(By.TAG_NAME, "p")
                                ))
                            except Exception as e:
                                print(f"Error getting description: {e}")
                            
                            events.append(Event(
                                title=title,
                                start_date=start_date,
                                end_date=end_date,
                                location=location,
                                month=month,
                                day=day,
                                description=description,
                                venue=location
                            ))
                            print(f"Added Agadir event: {title}")
                        else:
                            print(f"Skipping non-Agadir location: {location}")
                            
                    finally:
                        # Always return to main page
                        driver.get(initial_url)
                        wait.until(EC.url_to_be(initial_url))
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"Error processing event: {e}")
                    driver.get(initial_url)
                    wait.until(EC.url_to_be(initial_url))
                    time.sleep(2)
                    
            return events

        # Process events with better error handling
        events = process_events()

        # Print events with better formatting
        print("\nUpcoming Events at Orange Digital Center Agadir:")
        print("=" * 50)
        if not events:
            print("No Agadir events found")
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
        try:
            # Clear browser cache before quitting
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
            driver.quit()
        except:
            pass

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
