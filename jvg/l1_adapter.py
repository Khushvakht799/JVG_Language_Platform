"""
l1_adapter.py — Адаптер L1 (Реальность → JVG)
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class L1Adapter:
    def __init__(self):
        self.compiler = None

    def event_to_jvg(self, event: Dict[str, Any]) -> Dict[str, Any]:
        jvg = {
            "vectorograph": {
                "meta": {
                    "version": "1.0",
                    "title": event.get("title", "Событие"),
                    "date": event.get("timestamp", datetime.now().isoformat()),
                    "author": event.get("source", "L1"),
                    "status": "черновик"
                },
                "entity": {
                    "name": event.get("entity", "событие"),
                    "type": self._detect_type(event),
                    "purpose": event.get("purpose", "обработка события")
                },
                "context": {
                    "origin": event.get("origin", "L1"),
                    "environment": event.get("environment", "система"),
                    "dependencies": event.get("dependencies", [])
                },
                "structure": {
                    "components": event.get("components", []),
                    "layers": event.get("layers", [])
                },
                "relations": {
                    "inputs": event.get("inputs", []),
                    "outputs": event.get("outputs", []),
                    "connected_to": event.get("connections", [])
                },
                "logic": {
                    "rules": event.get("rules", []),
                    "algorithms": event.get("algorithms", []),
                    "decision_model": event.get("decision_model", [])
                },
                "state": {
                    "current": "ИССЛЕДОВАНИЕ",
                    "problems": event.get("problems", []),
                    "risks": event.get("risks", [])
                },
                "actions": {
                    "next_steps": event.get("actions", []),
                    "required_resources": event.get("resources", [])
                },
                "evolution": {
                    "history": f"Создано из события: {event.get('id', '')}",
                    "future_versions": []
                }
            }
        }
        return jvg

    def _detect_type(self, event: Dict[str, Any]) -> str:
        if "system" in str(event).lower():
            return "система"
        elif "process" in str(event).lower() or "процесс" in str(event).lower():
            return "процесс"
        elif "agent" in str(event).lower() or "агент" in str(event).lower():
            return "агент"
        return "идея"

    def log_to_jvg(self, log_line: str) -> Dict[str, Any]:
        return self.event_to_jvg({
            "title": "Лог события",
            "entity": "лог",
            "origin": "логирование",
            "description": log_line
        })

    def message_to_jvg(self, message: str, source: str = "пользователь") -> Dict[str, Any]:
        return self.event_to_jvg({
            "title": f"Сообщение от {source}",
            "entity": "сообщение",
            "origin": source,
            "purpose": "понимание запроса",
            "actions": ["обработать запрос"]
        })
