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
from pathlib import Path

@dataclass
class Event:
    title: str
    start_date: str
    end_date: str
    location: str
    month: str
    day: str
    description: str = ""

class EventScraper:
    def __init__(self):
        self.url = "https://www.orangedigitalcenters.com/country/ma/events"
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.events_file = self.data_dir / "events.txt"
        self.data_dir.mkdir(exist_ok=True)

    def scrape_events(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(self.url)

        events = self.get_event_list(driver)
        driver.quit()

        self._save_events(events)
        return events

    def get_event_list(self, driver):
        events = []
        wait = WebDriverWait(driver, 10)
        event_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'event-detail')))

        for event_element in event_elements:
            try:
                month = event_element.find_element(By.CLASS_NAME, 'alphabetic-month').text.strip()
                day = event_element.find_element(By.CLASS_NAME, 'numeric-date').text.strip()
                title = event_element.find_element(By.CLASS_NAME, 'event-title').text.strip()
                dates = event_element.find_elements(By.CLASS_NAME, 'from-to-date-wrapper')
                start_date = dates[0].text.replace('De ', '').strip()
                end_date = dates[1].text.replace('À ', '').strip()
                location = 'ODC Agadir' if 'Agadir' in title else 'ODC Other'

                event_element.click()
                self.wait_for_detail_page(driver)
                description = self.get_clean_description(driver)
                driver.back()

                event = Event(
                    title=title,
                    start_date=start_date,
                    end_date=end_date,
                    location=location,
                    month=month,
                    day=day,
                    description=description
                )
                events.append(event.__dict__)
            except StaleElementReferenceException:
                continue

        return events

    def wait_for_element(self, driver, by, value, timeout=10):
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))

    def wait_for_detail_page(self, driver, timeout=10):
        self.wait_for_element(driver, By.CLASS_NAME, 'event-detail-page', timeout)

    def get_clean_description(self, driver):
        description_element = self.wait_for_element(driver, By.CLASS_NAME, 'event-description')
        return description_element.text.strip()

    def _save_events(self, events):
        print(f"Saving events to {self.events_file}")
        with open(self.events_file, 'w', encoding='utf-8') as f:
            f.write("Upcoming Events at Orange Digital Center:\n\n")
            for event in events:
                f.write(f"Event: {event['title']}\n")
                f.write(f"Date: {event['month']} {event['day']}\n")
                f.write(f"From: {event['start_date']}\n")
                f.write(f"To: {event['end_date']}\n")
                f.write(f"Location: {event['location']}\n")
                f.write(f"Description: {event['description']}\n")
                f.write("\n---\n\n")
