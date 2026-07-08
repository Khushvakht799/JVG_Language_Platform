"""
referential_validator.py — L3: Ссылочная валидация JVG
"""

from typing import Dict, Any, List, Tuple
import re

class ReferentialValidator:
    def validate(self, jvg: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        data = jvg.get("vectorograph", {})
        entity = data.get("entity", {})
        logic = data.get("logic", {})

        if "id" in entity:
            uid = entity["id"]
            if not re.match(r'^jvg://[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+', uid):
                errors.append(f"Некорректный формат UID: {uid}")

        for rule in logic.get("rules", []):
            if isinstance(rule, dict) and "ref" in rule:
                errors.append(f"Ссылка на объект в правиле требует проверки: {rule['ref']}")

        return len(errors) == 0, errors
