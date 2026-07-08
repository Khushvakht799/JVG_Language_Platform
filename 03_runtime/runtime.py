"""
runtime.py — Среда исполнения JVG
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, '01_toolchain', 'storage'))
from store import JVGStore

class JVGRuntime:
    def __init__(self, storage_dir: str = "jvg_store"):
        self.store = JVGStore(storage_dir=storage_dir)
        self.state_transitions = {
            "ИССЛЕДОВАНИЕ": ["ПРОЕКТИРОВАНИЕ", "ОТЛОЖЕНО"],
            "ПРОЕКТИРОВАНИЕ": ["ВЫПОЛНЕНИЕ", "ЗАБЛОКИРОВАНО", "ОТЛОЖЕНО"],
            "ВЫПОЛНЕНИЕ": ["ЗАВЕРШЕНО", "ЗАБЛОКИРОВАНО", "ОТЛОЖЕНО"],
            "ЗАБЛОКИРОВАНО": ["ВЫПОЛНЕНИЕ", "ОТЛОЖЕНО"],
            "ЗАВЕРШЕНО": [],
            "ОТЛОЖЕНО": ["ИССЛЕДОВАНИЕ", "ПРОЕКТИРОВАНИЕ", "ВЫПОЛНЕНИЕ"]
        }

    def step(self, doc_id: str, new_state: Optional[str] = None, action_result: Optional[str] = None) -> Dict[str, Any]:
        jvg = self.store.get(doc_id)
        if not jvg:
            return {"status": "error", "error": f"Документ {doc_id} не найден"}

        data = jvg.get("vectorograph", {})
        state = data.get("state", {})
        evolution = data.get("evolution", {})
        current_state = state.get("current", "ИССЛЕДОВАНИЕ")
        changes = []
        result = {"status": "ok", "doc_id": doc_id, "old_state": current_state, "new_state": current_state, "changes": changes}

        if new_state and new_state != current_state:
            if new_state in self.state_transitions.get(current_state, []):
                state["current"] = new_state
                result["new_state"] = new_state
                changes.append(f"Переход: {current_state} → {new_state}")
                history_entry = f"[{datetime.now().isoformat()}] Переход: {current_state} → {new_state}"
                if evolution.get("history"):
                    evolution["history"] += "\n" + history_entry
                else:
                    evolution["history"] = history_entry
            else:
                result["status"] = "warning"
                result["error"] = f"Недопустимый переход: {current_state} → {new_state}"
                return result

        if action_result:
            history_entry = f"[{datetime.now().isoformat()}] Действие выполнено: {action_result}"
            if evolution.get("history"):
                evolution["history"] += "\n" + history_entry
            else:
                evolution["history"] = history_entry
            changes.append(f"Действие: {action_result}")

        if changes:
            jvg["vectorograph"]["state"] = state
            jvg["vectorograph"]["evolution"] = evolution
            updated_id = self.store.save(jvg)
            result["updated_doc_id"] = updated_id
            result["changes"] = changes

        return result

    def run(self, doc_id: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        history = []
        current_doc_id = doc_id
        for i, step in enumerate(steps):
            print(f"  Шаг {i+1}: {step}")
            result = self.step(current_doc_id, new_state=step.get("new_state"), action_result=step.get("action_result"))
            history.append(result)
            if result["status"] == "error":
                break
            if "updated_doc_id" in result:
                current_doc_id = result["updated_doc_id"]
        return {"status": "ok", "doc_id": doc_id, "final_doc_id": current_doc_id, "steps": history}

    def get_history(self, doc_id: str) -> List[str]:
        jvg = self.store.get(doc_id)
        if not jvg:
            return []
        evolution = jvg.get("vectorograph", {}).get("evolution", {})
        history_text = evolution.get("history", "")
        if history_text:
            return [h.strip() for h in history_text.split("\n") if h.strip()]
        return []

    def get_state(self, doc_id: str) -> str:
        jvg = self.store.get(doc_id)
        if not jvg:
            return "unknown"
        return jvg.get("vectorograph", {}).get("state", {}).get("current", "unknown")

def test_runtime():
    from store import JVGStore
    store = JVGStore(storage_dir="test_store")
    test_jvg = {
        "vectorograph": {
            "meta": {"version": "1.0", "title": "Тестовый процесс", "date": "2026-07-07", "author": "Тестер", "status": "черновик"},
            "entity": {"name": "Процесс", "type": "процесс", "purpose": "тестирование Runtime"},
            "context": {"origin": "тест", "environment": "локальная среда", "dependencies": []},
            "structure": {"components": [], "layers": []},
            "relations": {"inputs": [], "outputs": [], "connected_to": []},
            "logic": {"rules": [], "algorithms": [], "decision_model": []},
            "state": {"current": "ИССЛЕДОВАНИЕ", "problems": [], "risks": []},
            "actions": {"next_steps": ["протестировать", "развернуть"], "required_resources": ["сервер"]},
            "evolution": {"history": "начало", "future_versions": []}
        }
    }
    doc_id = store.save(test_jvg)
    print(f"Создан документ: {doc_id}")
    runtime = JVGRuntime(storage_dir="test_store")
    print("\n=== Выполняем шаги ===")
    result = runtime.run(doc_id, [
        {"new_state": "ПРОЕКТИРОВАНИЕ", "action_result": "начало проектирования"},
        {"new_state": "ВЫПОЛНЕНИЕ", "action_result": "запуск реализации"},
        {"new_state": "ЗАВЕРШЕНО", "action_result": "проект завершён"}
    ])
    print(f"\nРезультат: {result['status']}")
    print(f"Финальный документ: {result['final_doc_id']}")
    history = runtime.get_history(result['final_doc_id'])
    print("\n=== История ===")
    for entry in history:
        print(f"  {entry}")

if __name__ == "__main__":
    test_runtime()
