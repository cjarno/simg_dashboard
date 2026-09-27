import json
import os
from datetime import datetime
from typing import Any, Dict


def load_json(path: str) -> Dict:
    """Load JSON file"""
    full_path = os.path.join(os.path.dirname(__file__), '..', '..', path)
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(path: str, data: Dict) -> None:
    """Save data to JSON file"""
    full_path = os.path.join(os.path.dirname(__file__), '..', '..', path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + 'Z'


def log_event(event: str, details: Dict = None) -> None:
    """Log event to session log"""
    log_path = os.path.join(os.path.dirname(__file__), '..', '..', '.simg_state', 'session_log.json')
    log_data = load_json(log_path)
    log_data['last_updated'] = get_timestamp()
    
    event_record = {
        'timestamp': get_timestamp(),
        'event': event,
        'details': details or {}
    }
    log_data['events'].append(event_record)
    
    save_json(log_path, log_data)


def generate_uuid() -> str:
    """Generate a simple UUID-like string"""
    import uuid
    return str(uuid.uuid4())[:8]
