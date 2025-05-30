import os
import json
import argparse
from typing import Dict, Any, List, Optional

DEFAULT_CONFIG_PATH = "config/events.json"
DEFAULT_GROUND_TRUTH_PATH = "config/ground_truth.json"

class EventConfig:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize EventConfig with optional custom config path."""
        self.config_path = config_path or "config/events.json"
        self.events = self._load_config()
    
    def _load_config(self) -> Dict[str, Dict[str, Any]]:
        """Load event configuration from JSON file."""
        if not os.path.exists(self.config_path):
            # Create default config if it doesn't exist
            default_config = {
                "Acquisition": {"relevant": True},
                "Customer Event": {"relevant": True},
                "Personnel Change": {"relevant": True},
                "Financial Event": {"relevant": True},
                "Open Market Purchase": {"relevant": True},
                "Open Market Sale": {"relevant": True},
                "Option Exercise": {"relevant": True},
                "Shares Withheld for Taxes": {"relevant": False},
                "Automatic Sale under Rule 10b5-1": {"relevant": False},
                "Other": {"relevant": False}
            }
            self._save_config(default_config)
            return default_config
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_config(self, config: Dict[str, Dict[str, Any]]) -> None:
        """Save event configuration to JSON file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def add_event_type(self, event_type: str, relevant: bool = True) -> None:
        """Add a new event type to the configuration."""
        self.events[event_type] = {"relevant": relevant}
        self._save_config(self.events)
    
    def remove_event_type(self, event_type: str) -> None:
        """Remove an event type from the configuration."""
        if event_type in self.events:
            del self.events[event_type]
            self._save_config(self.events)
    
    def update_relevance(self, event_type: str, relevant: bool) -> None:
        """Update the relevance of an event type."""
        if event_type in self.events:
            self.events[event_type]["relevant"] = relevant
            self._save_config(self.events)
    
    def get_event_types(self) -> List[str]:
        """Get list of configured event types."""
        return list(self.events.keys())
    
    def is_relevant(self, event_type: str) -> bool:
        """Check if an event type is marked as relevant by default."""
        return self.events.get(event_type, {}).get("relevant", False)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments for configuration."""
    parser = argparse.ArgumentParser(description="SEC 8-K Event Classifier Configuration")
    parser.add_argument('--config', type=str, default=DEFAULT_CONFIG_PATH,
                      help='Path to event configuration file')
    parser.add_argument('--add-event', type=str, nargs=2, metavar=('EVENT_TYPE', 'RELEVANT'),
                      help='Add a new event type (e.g., --add-event "New Event" true)')
    parser.add_argument('--remove-event', type=str,
                      help='Remove an event type')
    parser.add_argument('--update-relevance', type=str, nargs=2, metavar=('EVENT_TYPE', 'RELEVANT'),
                      help='Update event type relevance (e.g., --update-relevance "Event" false)')
    parser.add_argument('--list-events', action='store_true',
                      help='List all configured event types')
    return parser.parse_args()

def main():
    """Main function for configuration management."""
    args = parse_args()
    config = EventConfig(args.config)
    
    if args.add_event:
        event_type, relevant = args.add_event
        config.add_event_type(event_type, relevant.lower() == 'true')
        print(f"Added event type: {event_type}")
    
    if args.remove_event:
        config.remove_event_type(args.remove_event)
        print(f"Removed event type: {args.remove_event}")
    
    if args.update_relevance:
        event_type, relevant = args.update_relevance
        config.update_relevance(event_type, relevant.lower() == 'true')
        print(f"Updated relevance for {event_type}")
    
    if args.list_events:
        print("\nConfigured Event Types:")
        for event_type in config.get_event_types():
            relevant = config.is_relevant(event_type)
            print(f"- {event_type} (Default Relevant: {relevant})")

if __name__ == "__main__":
    main() 