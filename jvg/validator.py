"""
validator.py — Валидатор JVG
"""

import sys
import os
from typing import Dict, Any, List, Tuple

from .config import STORAGE_DIR

class JVGValidatorPipeline:
    def __init__(self):
        self.structural_errors = []
        self.semantic_errors = []

    def validate(self, jvg: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        data = jvg.get("vectorograph", {})
        
        # Проверяем наличие обязательных секций
        required_sections = ["meta", "entity", "context", "structure", "relations", "logic", "state", "actions", "evolution"]
        for section in required_sections:
            if section not in data:
                errors.append(f"Отсутствует обязательная секция: {section}")
        
        # Проверяем entity
        entity = data.get("entity", {})
        if not entity.get("name"):
            errors.append("Отсутствует имя сущности (entity.name)")
        if not entity.get("type"):
            errors.append("Отсутствует тип сущности (entity.type)")
        if entity.get("type") not in ["система", "процесс", "идея", "агент"]:
            errors.append(f"Недопустимый тип: {entity.get('type')}")

        # Проверяем state
        state = data.get("state", {})
        if state.get("current") and state.get("current") not in ["ИССЛЕДОВАНИЕ", "ПРОЕКТИРОВАНИЕ", "ВЫПОЛНЕНИЕ", "ЗАБЛОКИРОВАНО", "ЗАВЕРШЕНО", "ОТЛОЖЕНО", "ОЖИДАНИЕ", "НЕСТАБИЛЬНО"]:
            errors.append(f"Недопустимое состояние: {state.get('current')}")

        return len(errors) == 0, errors
