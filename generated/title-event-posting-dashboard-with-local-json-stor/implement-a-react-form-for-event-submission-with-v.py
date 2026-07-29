import os
import json
from datetime import datetime

class Event:
    def __init__(self, title, date, time, description, venue, category):
        self.title = title
        self.date = date
        self.time = time
        self.description = description
        self.venue = venue
        self.category = category

def validate_event(event):
    if not all([event.title, event.date, event.time, event.description, event.venue]):
        return False, "All fields are required."
    try:
        datetime.strptime(event.date, "%Y-%m-%d")
        datetime.strptime(event.time, "%H:%M")
    except ValueError:
        return False, "Invalid date or time format. Use YYYY-MM-DD and HH:MM."
    if event.category not in ["show", "movie", "other"]:
        return False, "Category must be 'show', 'movie', or 'other'."
    return True, ""

def save_events(events, file_path="events.json"):
    with open(file_path, "w") as f:
        json.dump([event.__dict__ for event in events], f)

def load_events(file_path="events.json"):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        data = json.load(f)
        return [Event(**event) for event in data]