"""
jvg/knowledge/world_model.py — Модель мира для планировщика
"""

from typing import Dict, Any, List, Optional
from ..storage.store import JVGStore

class WorldModel:
    def __init__(self, store: Optional[JVGStore] = None):
        self.store = store or JVGStore()

    def collect_facts(self, doc_id: Optional[str] = None) -> Dict[str, Any]:
        facts = {
            "agents": {},
            "system": {
                "timestamp": __import__("time").strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        items = self.store.list()
        for item in items:
            if doc_id and item.get("id") != doc_id:
                continue

            jvg = self.store.get(item.get("id"))
            if not jvg:
                continue

            data = jvg.get("vectorograph", {})
            meta = data.get("meta", {})
            entity = data.get("entity", {})
            state = data.get("state", {})
            evolution = data.get("evolution", {})

            agent_name = entity.get("name", item.get("id"))
            current_state = state.get("current", "unknown")

            last_fact = None
            history = evolution.get("history", "")
            if history:
                lines = history.strip().split("\n")
                for line in reversed(lines):
                    if "Факты:" in line:
                        try:
                            fact_part = line.split("Факты:")[1].strip()
                            last_fact = eval(fact_part)
                        except:
                            pass
                        break

            facts["agents"][agent_name] = {
                "id": item.get("id"),
                "state": current_state,
                "type": entity.get("type", "unknown"),
                "purpose": entity.get("purpose", ""),
                "last_fact": last_fact,
                "history_length": len(history.split("\n")) if history else 0
            }

        return facts

    def get_agent_state(self, doc_id: str) -> str:
        jvg = self.store.get(doc_id)
        if not jvg:
            return "unknown"
        return jvg.get("vectorograph", {}).get("state", {}).get("current", "unknown")

    def get_agent_facts(self, doc_id: str) -> Dict[str, Any]:
        jvg = self.store.get(doc_id)
        if not jvg:
            return {}
        evolution = jvg.get("vectorograph", {}).get("evolution", {})
        history = evolution.get("history", "")
        if not history:
            return {}
        
        lines = history.strip().split("\n")
        for line in reversed(lines):
            if "Факты:" in line:
                try:
                    fact_part = line.split("Факты:")[1].strip()
                    return eval(fact_part)
                except:
                    pass
        return {}
