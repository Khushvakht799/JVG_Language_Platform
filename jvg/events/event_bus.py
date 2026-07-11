"""
jvg/events/event_bus.py — Шина событий между агентами
"""

from typing import Dict, Any, List, Callable
from datetime import datetime

class EventBus:
    _subscribers: Dict[str, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: str, callback: Callable):
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(callback)

    @classmethod
    def publish(cls, event_type: str, data: Dict[str, Any]):
        print(f"📡 Событие: {event_type} → {data}")
        for callback in cls._subscribers.get(event_type, []):
            callback(data)

    @classmethod
    def clear(cls):
        cls._subscribers.clear()
