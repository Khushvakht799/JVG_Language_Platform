"""
jvg/runtime/executor.py — Исполнитель с правильной последовательностью
"""

from typing import Dict, Any, Optional
from datetime import datetime
from ..storage.store import JVGStore
from ..fsm.fsm_engine import FSMEngine
from ..execution.action_executor import ActionExecutor
from ..identity.identity import Identity

class JVGExecutor:
    def __init__(self, storage_dir: Optional[str] = None, debug: bool = False):
        self.store = JVGStore(storage_dir=storage_dir)
        self.executor = ActionExecutor()
        self.debug = debug

    def _log(self, step: int, message: str, data: Any = None):
        if self.debug:
            print(f"[{step}] {message}")
            if data is not None:
                print(f"     {data}")

    def execute(self, doc_id: str) -> Dict[str, Any]:
        self._log(1, "Загрузка документа", doc_id)
        jvg = self.store.get(doc_id)
        if not jvg:
            return {"status": "error", "error": f"Документ {doc_id} не найден"}

        self._log(2, "Документ загружен", jvg.get("vectorograph", {}).get("meta", {}).get("title", "без названия"))

        fsm = FSMEngine(jvg)
        data = jvg.get("vectorograph", {})
        state = data.get("state", {})
        current_state = state.get("current", fsm.get_initial_state())

        self._log(3, "Текущее состояние", current_state)
        available = fsm.get_available_transitions(current_state)
        self._log(4, "Доступные переходы", available)
        self._log(5, "Все состояния", fsm.states)

        if not available:
            return {
                "status": "idle",
                "doc_id": doc_id,
                "state": current_state,
                "message": "Нет доступных переходов",
                "available": available,
                "states": fsm.states
            }

        next_state = available[0]
        self._log(6, "Выбран следующий переход", next_state)

        # 1. Сначала обновляем состояние
        state["current"] = next_state
        history_entry = f"[{datetime.now().isoformat()}] Переход: {current_state} → {next_state}"
        evolution = data.get("evolution", {})
        evolution["history"] = evolution.get("history", "") + "\n" + history_entry

        jvg["vectorograph"]["state"] = state
        jvg["vectorograph"]["evolution"] = evolution
        jvg = Identity.version(jvg, next_state)

        self._log(7, "Состояние обновлено", f"{current_state} → {next_state}")

        # 2. Применяем правила ДЛЯ НОВОГО состояния
        rules = fsm.get_rules()
        self._log(8, f"Правил: {len(rules)}", rules)

        action_executed = False
        for rule in rules:
            condition = rule.get("condition", "")
            self._log(9, "Проверка условия", condition)
            if "state == " in condition:
                expected_state = condition.split("state == ")[1].strip().strip('"')
                self._log(10, "Ожидаемое состояние", expected_state)
                if state.get("current") == expected_state:
                    action = rule.get("action")
                    params = rule.get("action_params", {})
                    self._log(11, f"Применяем правило: {condition} → {action}", params)
                    exec_result = self.executor.execute(action, params)
                    self._log(12, "Результат выполнения", exec_result)
                    if exec_result.get("status") == "ok":
                        # Добавляем в историю
                        evolution = jvg["vectorograph"].get("evolution", {})
                        history_entry = f"[{datetime.now().isoformat()}] Выполнено действие: {action}"
                        evolution["history"] = evolution.get("history", "") + "\n" + history_entry
                        jvg["vectorograph"]["evolution"] = evolution
                        self.store.update(doc_id, jvg)
                        action_executed = True
                    break

        if not action_executed:
            self._log(13, "Действие не выполнено (нет подходящих правил для нового состояния)")

        # 3. Сохраняем финальную версию
        self.store.update(doc_id, jvg)
        self._log(14, "Документ сохранён", next_state)

        return {
            "status": "ok",
            "doc_id": doc_id,
            "old_state": current_state,
            "new_state": next_state,
            "updated_doc_id": doc_id,
            "version": jvg["vectorograph"]["meta"].get("version", "0"),
            "available": fsm.get_available_transitions(next_state),
            "action_executed": action_executed
        }

    def get_state(self, doc_id: str) -> str:
        jvg = self.store.get(doc_id)
        if not jvg:
            return "unknown"
        fsm = FSMEngine(jvg)
        return jvg.get("vectorograph", {}).get("state", {}).get("current", fsm.get_initial_state())
