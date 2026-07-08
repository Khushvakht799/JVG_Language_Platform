"""
behavioral_validator.py — L4: Поведенческая валидация JVG
"""

from typing import Dict, Any, List, Tuple

class BehavioralValidator:
    def validate(self, jvg: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        data = jvg.get("vectorograph", {})
        actions = data.get("actions", {})
        logic = data.get("logic", {})
        verbs = ["собрать", "проверить", "запустить", "протестировать", "развернуть", "настроить", "установить"]

        for step in actions.get("next_steps", []):
            if isinstance(step, str) and not any(step.startswith(v) for v in verbs):
                errors.append(f"Действие должно начинаться с глагола: '{step}'")

        for rule in logic.get("rules", []):
            if isinstance(rule, str) and "→" not in rule:
                errors.append(f"Правило должно содержать условие и следствие (→): '{rule}'")

        return len(errors) == 0, errors
