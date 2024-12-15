from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests

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
    try:
        print("Fetching events...")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        events = []
        event_divs = soup.find_all('div', class_='event-detail')
        
        for event_div in event_divs:
            try:
                # Extract month and day
                month = event_div.find('p', class_='alphabetic-month').text.strip()
                day = event_div.find('h5', class_='numeric-date').text.strip()
                
                # Extract event details
                title = event_div.find('h5', class_='event-title').text.strip()
                dates = event_div.find_all('p', class_='from-to-date-wrapper')
                start_date = dates[0].text.strip() if dates else "N/A"
                end_date = dates[1].text.strip() if len(dates) > 1 else "N/A"
                
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
                events.append(event)
                
            except Exception as e:
                print(f"Error parsing event: {e}")
                continue
        
        # Print events in a formatted way
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

if __name__ == "__main__":
    test_scrape_events()
