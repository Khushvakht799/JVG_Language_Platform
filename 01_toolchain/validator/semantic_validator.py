"""
semantic_validator.py — L2: Семантическая валидация JVG
"""

from typing import Dict, Any, List, Tuple

class SemanticValidator:
    def validate(self, jvg: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        data = jvg.get("vectorograph", {})
        entity = data.get("entity", {})
        actions = data.get("actions", {})
        state = data.get("state", {})
        evolution = data.get("evolution", {})

        if entity.get("type") == "агент" and not actions.get("next_steps"):
            errors.append("Агент должен иметь хотя бы одно действие в actions.next_steps")
        if state.get("current") == "ЗАВЕРШЕНО" and not evolution.get("history"):
            errors.append("Завершённый объект должен иметь историю в evolution.history")
        if not entity.get("name") and not actions.get("next_steps"):
            errors.append("Объект без имени и действий выглядит пустым")

        return len(errors) == 0, errors
