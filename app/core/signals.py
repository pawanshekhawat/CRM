from typing import Callable, Dict, List
import logging

logger = logging.getLogger("CRM.Signals")

class EventBus:
    """A lightweight event dispatcher to decouple modules and components."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable):
        if event_name in self._subscribers:
            self._subscribers[event_name] = [cb for cb in self._subscribers[event_name] if cb != callback]

    def emit(self, event_name: str, *args, **kwargs):
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing callback for event '{event_name}': {e}", exc_info=True)

# Global event bus instance
event_bus = EventBus()
