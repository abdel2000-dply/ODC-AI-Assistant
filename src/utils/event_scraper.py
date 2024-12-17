from dataclasses import dataclass
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

@dataclass
class Event:
    title: str
    start_date: str
    end_date: str
    location: str
    month: str
    day: str

class EventScraper:
    def __init__(self):
        self.url = "https://www.orangedigitalcenters.com/country/ma/events"
        # Update path to use data directory
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.events_file = self.data_dir / "events.txt"
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)

    def scrape_events(self):
        try:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            events = []
            event_divs = soup.find_all('div', class_='event-detail')
            
            for event_div in event_divs:
                # Extract month and day
                month = event_div.find('p', class_='alphabetic-month').text.strip()
                day = event_div.find('h5', class_='numeric-date').text.strip()
                
                # Extract event details
                title = event_div.find('h5', class_='event-title').text.strip()
                dates = event_div.find_all('p', class_='from-to-date-wrapper')
                start_date = dates[0].text.replace('De ', '').strip()
                end_date = dates[1].text.replace('À ', '').strip()
                
                # Determine location from title
                location = 'ODC Agadir' if 'Agadir' in title else 'ODC Other'
                
                event = Event(
                    title=title,
                    start_date=start_date,
                    end_date=end_date,
                    location=location,
                    month=month,
                    day=day
                )
                events.append(event.__dict__)
            
            # Save events to file
            self._save_events(events)
            return events
            
        except Exception as e:
            print(f"Error scraping events: {e}")
            return []

    def _save_events(self, events):
        # Save as formatted text for RAG processing
        print(f"Saving events to {self.events_file}")
        with open(self.events_file, 'w', encoding='utf-8') as f:
            f.write("Upcoming Events at Orange Digital Center:\n\n")
            for event in events:
                f.write(f"Event: {event['title']}\n")
                f.write(f"Date: {event['month']} {event['day']}\n")
                f.write(f"From: {event['start_date']}\n")
                f.write(f"To: {event['end_date']}\n")
                f.write(f"Location: {event['location']}\n")
                f.write("\n---\n\n")
