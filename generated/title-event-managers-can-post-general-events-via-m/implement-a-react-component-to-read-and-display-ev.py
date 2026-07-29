import json
import os
from pathlib import Path

def load_events_file(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Events file not found: {file_path}")
    with file_path.open() as f:
        return json.load(f)

def get_formatted_events(events_data):
    if not events_data:
        return []
    formatted_events = []
    for event in events_data:
        formatted_event = {
            "title": event.get("title", ""),
            "date": event.get("date", ""),
            "description": event.get("description", ""),
            "media": event.get("media", [])
        }
        formatted_events.append(formatted_event)
    return formatted_events