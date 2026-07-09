"""
jvg/runtime/runtime.py — Среда исполнения JVG с FSM
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from ..storage.store import JVGStore
from ..execution.action_executor import ActionExecutor
from ..identity.identity import Identity
from ..fsm.fsm_engine import FSMEngine

class JVGRuntime:
    def __init__(self, storage_dir: Optional[str] = None):
        self.store = JVGStore(storage_dir=storage_dir)
        self.executor = ActionExecutor()

    def step(self, doc_id: str, new_state: Optional[str] = None,
             action_result: Optional[str] = None) -> Dict[str, Any]:
        jvg = self.store.get(doc_id)
        if not jvg:
            return {"status": "error", "error": f"Документ {doc_id} не найден"}

        # Загружаем FSM
        fsm = FSMEngine(jvg)
        data = jvg.get("vectorograph", {})
        state = data.get("state", {})
        evolution = data.get("evolution", {})
        current_state = state.get("current", fsm.get_initial_state())

        # Проверяем переход
        if new_state and not fsm.can_transition(current_state, new_state):
            available = fsm.get_available_transitions(current_state)
            return {
                "status": "warning",
                "doc_id": doc_id,
                "old_state": current_state,
                "new_state": current_state,
                "error": f"Недопустимый переход: {current_state} → {new_state}",
                "available": available
            }

        # Выполняем переход
        if new_state and new_state != current_state:
            state["current"] = new_state
            history_entry = f"[{datetime.now().isoformat()}] Переход: {current_state} → {new_state}"
            evolution["history"] = evolution.get("history", "") + "\n" + history_entry

        if action_result:
            history_entry = f"[{datetime.now().isoformat()}] Действие: {action_result}"
            evolution["history"] = evolution.get("history", "") + "\n" + history_entry

        jvg["vectorograph"]["state"] = state
        jvg["vectorograph"]["evolution"] = evolution
        
        # Обновляем версию
        jvg = Identity.version(jvg, new_state or current_state)

        updated_id = self.store.save(jvg)

        result = {
            "status": "ok",
            "doc_id": doc_id,
            "old_state": current_state,
            "new_state": state.get("current"),
            "updated_doc_id": updated_id,
            "version": jvg["vectorograph"]["meta"].get("version", "0"),
            "available": fsm.get_available_transitions(state.get("current"))
        }

        # Проверяем правила
        rules = fsm.get_rules()
        for rule in rules:
            condition = rule.get("condition", "")
            if "state == " in condition:
                expected_state = condition.split("state == ")[1].strip().strip('"')
                if state.get("current") == expected_state:
                    action = rule.get("action")
                    params = rule.get("action_params", {})
                    print(f"   🔧 Применяем правило: {condition} → {action}")
                    exec_result = self.executor.execute(action, params)
                    if exec_result.get("status") == "ok":
                        history_entry = f"[{datetime.now().isoformat()}] Выполнено действие: {action}"
                        jvg["vectorograph"]["evolution"]["history"] = jvg["vectorograph"]["evolution"].get("history", "") + "\n" + history_entry
                        self.store.save(jvg)
                    result["action_result"] = exec_result

        return result

    def get_state(self, doc_id: str) -> str:
        jvg = self.store.get(doc_id)
        if not jvg:
            return "unknown"
        fsm = FSMEngine(jvg)
        current = jvg.get("vectorograph", {}).get("state", {}).get("current", fsm.get_initial_state())
        return current
