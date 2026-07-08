"""
l5_audit.py — Слой аудита L5
"""

import os
import sys
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, '01_toolchain', 'validator'))
from validator_pipeline import JVGValidatorPipeline

class L5Audit:
    def __init__(self):
        self.validator = JVGValidatorPipeline()

    def validate(self, jvg: Dict[str, Any]) -> Dict[str, Any]:
        valid, errors = self.validator.validate(jvg)
        return {"valid": valid, "errors": errors, "errors_count": len(errors)}

    def explain(self, doc_id: str, jvg: Dict[str, Any]) -> str:
        data = jvg.get("vectorograph", {})
        entity = data.get("entity", {})
        state = data.get("state", {})
        evolution = data.get("evolution", {})
        return (
            f"Объект: {entity.get('name', 'неизвестен')}\n"
            f"Тип: {entity.get('type', 'неизвестен')}\n"
            f"Состояние: {state.get('current', 'неизвестно')}\n"
            f"Проблемы: {', '.join(state.get('problems', ['нет']))}\n"
            f"Риски: {', '.join(state.get('risks', ['нет']))}\n"
            f"История: {evolution.get('history', 'нет')[:100]}..."
        )

    def get_history_report(self, doc_id: str, runtime) -> str:
        history = runtime.get_history(doc_id)
        if not history:
            return "История пуста"
        return "\n".join([f"  - {h}" for h in history[-5:]])
