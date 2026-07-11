"""
jvg/planning/router.py — Маршрутизатор событий
"""

from typing import Dict, Any, List, Callable
from ..events.event_bus import EventBus

class Router:
    _routes: Dict[str, List[Dict[str, Any]]] = {}

    @classmethod
    def register(cls, event_type: str, target_doc: str, condition: str = None, priority: int = 0):
        if event_type not in cls._routes:
            cls._routes[event_type] = []
        cls._routes[event_type].append({
            "target": target_doc,
            "condition": condition,
            "priority": priority
        })
        print(f"📌 Маршрут зарегистрирован: {event_type} → {target_doc}")

    @classmethod
    def route(cls, event_type: str, data: Dict[str, Any]) -> List[str]:
        routes = cls._routes.get(event_type, [])
        routes.sort(key=lambda x: x.get("priority", 0), reverse=True)
        targets = []
        for route in routes:
            condition = route.get("condition")
            if condition:
                if condition in str(data):
                    targets.append(route["target"])
            else:
                targets.append(route["target"])
        return targets
