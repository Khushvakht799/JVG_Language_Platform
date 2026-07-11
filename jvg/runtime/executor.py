"""
jvg/runtime/executor.py — Исполнитель с событиями (исправленный)
"""

from typing import Dict, Any, Optional
from datetime import datetime
import time
from ..storage.store import JVGStore
from ..fsm.fsm_engine import FSMEngine
from ..execution.action_executor import ActionExecutor
from ..execution.interpreter import SemanticInterpreter
from ..identity.identity import Identity
from ..events.event_bus import EventBus

class JVGExecutor:
    def __init__(self, storage_dir: Optional[str] = None, debug: bool = False, loop: bool = False):
        self.store = JVGStore(storage_dir=storage_dir)
        self.debug = debug
        self.loop = loop
        self.running = True

    def _log(self, step: int, message: str, data: Any = None):
        if self.debug:
            print(f"[{step}] {message}")
            if data is not None:
                print(f"     {data}")

    def _execute_once(self, doc_id: str) -> Dict[str, Any]:
        jvg = self.store.get(doc_id)
        if not jvg:
            return {"status": "error", "error": f"Документ {doc_id} не найден"}

        fsm = FSMEngine(jvg, debug=self.debug)
        data = jvg.get("vectorograph", {})
        state = data.get("state", {})
        current_state = state.get("current", fsm.get_initial_state())

        self._log(3, "Текущее состояние", current_state)
        transitions = fsm.get_available_transitions(current_state)
        self._log(4, "Доступные переходы", transitions)

        if not transitions:
            return {"status": "idle", "doc_id": doc_id, "state": current_state, "message": "Нет доступных переходов"}

        # Выполняем правила для текущего состояния
        rules = fsm.get_rules()
        action_result = None
        facts = None

        for rule in rules:
            condition = rule.get("condition", "")
            if condition.startswith("state == "):
                expected_state = condition.split("state == ")[1].strip().strip('"')
                if expected_state == current_state:
                    action = rule.get("action")
                    params = rule.get("action_params", {})
                    self._log(11, f"Применяем правило: {condition} → {action}", params)
                    action_result = ActionExecutor.execute(action, params)
                    self._log(12, "Результат выполнения", action_result.to_dict() if action_result else None)

                    facts = SemanticInterpreter.interpret(action_result) if action_result else {}
                    self._log(13, "Интерпретированные факты", facts)
                    break

        # Выбираем переход на основе фактов
        transition = fsm.get_transition_by_facts(current_state, facts or {})
        if not transition:
            return {"status": "idle", "doc_id": doc_id, "state": current_state, "message": "Нет подходящего перехода"}

        next_state = transition.get("to")
        condition_used = transition.get("condition", "нет условия")
        self._log(14, f"Выбран переход по условию", f"{current_state} → {next_state} (условие: {condition_used})")

        # Публикуем событие о переходе
        event_data = {
            "doc_id": doc_id,
            "from_state": current_state,
            "to_state": next_state,
            "condition": condition_used,
            "facts": facts,
            "action_result": action_result.to_dict() if action_result else None
        }
        EventBus.publish(f"transition.{current_state}_{next_state}", event_data)

        # Обновляем состояние
        state["current"] = next_state
        evolution = data.get("evolution", {})
        history_entry = f"[{datetime.now().isoformat()}] Переход: {current_state} → {next_state} (условие: {condition_used})"
        evolution["history"] = evolution.get("history", "") + "\n" + history_entry

        jvg["vectorograph"]["state"] = state
        jvg["vectorograph"]["evolution"] = evolution
        jvg = Identity.version(jvg, next_state)

        if action_result:
            history_entry = f"[{datetime.now().isoformat()}] Результат: {action_result.to_dict()}"
            jvg["vectorograph"]["evolution"]["history"] = jvg["vectorograph"]["evolution"].get("history", "") + "\n" + history_entry

        if facts:
            history_entry = f"[{datetime.now().isoformat()}] Факты: {facts}"
            jvg["vectorograph"]["evolution"]["history"] = jvg["vectorograph"]["evolution"].get("history", "") + "\n" + history_entry

        self.store.update(doc_id, jvg)
        self._log(17, "Документ сохранён", next_state)

        return {
            "status": "ok",
            "doc_id": doc_id,
            "old_state": current_state,
            "new_state": next_state,
            "condition_used": condition_used,
            "available": fsm.get_available_transitions(next_state),
            "action_result": action_result.to_dict() if action_result else None,
            "facts": facts
        }

    def _execute_loop(self, doc_id: str):
        print("🔄 Запуск живого мониторинга...")
        iteration = 0
        while self.running:
            iteration += 1
            print(f"\n--- Итерация {iteration} ---")
            result = self._execute_once(doc_id)

            if result.get("status") == "idle":
                print(f"ℹ️ Документ в состоянии {result.get('state')}, нет доступных переходов. Ждём...")
                time.sleep(5)
                continue

            if result.get("status") == "error":
                print(f"❌ Ошибка: {result.get('error')}")
                break

            old_state = result.get("old_state", "?")
            new_state = result.get("new_state", "?")
            print(f"✅ Переход: {old_state} → {new_state}")
            print(f"   Условие: {result.get('condition_used', 'нет')}")
            print(f"   Следующие действия: {result.get('available', [])}")

            time.sleep(2)

    def execute(self, doc_id: str) -> Dict[str, Any]:
        if self.loop:
            self._execute_loop(doc_id)
            return {"status": "ok", "doc_id": doc_id, "message": "Цикл остановлен"}
        return self._execute_once(doc_id)
