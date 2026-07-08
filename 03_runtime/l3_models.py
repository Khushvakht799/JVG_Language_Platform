"""
l3_models.py — Слой моделей L3
"""

from typing import Dict, Any, List, Optional

class L3Models:
    def __init__(self, memory):
        self.memory = memory

    def analyze_state(self, doc_id: str) -> Dict[str, Any]:
        jvg = self.memory.get(doc_id)
        if not jvg:
            return {"status": "error", "error": "Документ не найден"}
        state = jvg.get("vectorograph", {}).get("state", {})
        current = state.get("current", "unknown")
        problems = state.get("problems", [])
        risks = state.get("risks", [])
        return {
            "status": "ok",
            "state": current,
            "problems_count": len(problems),
            "risks_count": len(risks),
            "is_healthy": len(problems) == 0 and len(risks) < 2,
            "next_suggested_state": self._suggest_next_state(current)
        }

    def _suggest_next_state(self, current: str) -> str:
        transitions = {"ИССЛЕДОВАНИЕ": "ПРОЕКТИРОВАНИЕ", "ПРОЕКТИРОВАНИЕ": "ВЫПОЛНЕНИЕ", "ВЫПОЛНЕНИЕ": "ЗАВЕРШЕНО"}
        return transitions.get(current, "ИССЛЕДОВАНИЕ")

    def find_similar(self, doc_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        jvg = self.memory.get(doc_id)
        if not jvg:
            return []
        data = jvg.get("vectorograph", {})
        entity = data.get("entity", {})
        purpose = entity.get("purpose", "")
        return self.memory.search(purpose, top_k=top_k)
