import json
from pathlib import Path
from datetime import datetime
from .document_processor import DocumentProcessor
from test_scraper import test_scrape_events

class EventManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.events_file = self.base_dir / "data" / "events.json"
        self.doc_processor = DocumentProcessor()
        
    def update_events(self):
        """Scrape new events and update storage"""
        print("Updating events...")
        events = test_scrape_events()
        
        # Store events in JSON
        self.save_events(events)
        
        # Convert to text format for embedding
        self.create_event_documents()
        
        # Update vector store
        self.doc_processor.process_documents()
        
    def save_events(self, events):
        """Save events to JSON file"""
        event_data = {
            "last_updated": datetime.now().isoformat(),
            "events": [event.__dict__ for event in events]
        }
        
        self.events_file.parent.mkdir(exist_ok=True)
        with open(self.events_file, 'w', encoding='utf-8') as f:
            json.dump(event_data, f, ensure_ascii=False, indent=2)
            
    def create_event_documents(self):
        """Create text documents for embedding"""
        events_txt = self.base_dir / "data" / "events.txt"
        
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(events_txt, 'w', encoding='utf-8') as f:
                f.write("Orange Digital Center Agadir Events:\n\n")
                for event in data['events']:
                    f.write(f"Event: {event['title']}\n")
                    f.write(f"Date: {event['month']} {event['day']}\n")
                    f.write(f"Time: {event['start_date']} - {event['end_date']}\n")
                    f.write(f"Location: {event['location']}\n")
                    if event.get('description'):
                        f.write(f"Description:\n{event['description']}\n")
                    f.write("\n---\n\n")
                    
        except Exception as e:
            print(f"Error creating event documents: {e}")
