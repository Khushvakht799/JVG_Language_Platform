"""
jvg/agents/agent_runner.py — Универсальный исполнитель агентов (исправленное хранение)
"""

import time
from typing import Dict, Any, Optional
from ..storage.store import JVGStore
from ..fsm.fsm_engine import FSMEngine
from ..execution.action_executor import ActionExecutor
from ..execution.interpreter import SemanticInterpreter
from ..identity.identity import Identity
from ..events.event_bus import EventBus

class AgentRunner:
    def __init__(self, debug: bool = False, loop: bool = True):
        self.store = JVGStore()
        self.debug = debug
        self.loop = loop
        self.running = True

    def _log(self, step: int, message: str, data: Any = None):
        if self.debug:
            print(f"[{step}] {message}")
            if data is not None:
                print(f"     {data}")

    def _execute_rules(self, jvg: Dict[str, Any], current_state: str) -> tuple:
        fsm = FSMEngine(jvg, debug=self.debug)
        rules = fsm.get_rules()
        action_result = None
        facts = None
        next_state = None

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

                    transitions = fsm.get_available_transitions(current_state)
                    if transitions:
                        for t in transitions:
                            cond = t.get("condition")
                            if cond:
                                if fsm._evaluate_condition(cond, facts or {}):
                                    next_state = t.get("to")
                                    break
                        if not next_state:
                            next_state = transitions[0].get("to")
                    break

        return action_result, facts, next_state

    def run(self, doc_id: str) -> Dict[str, Any]:
        print(f"🤖 Запуск агента: {doc_id}")

        iteration = 0
        final_state = None
        current_doc_id = doc_id

        while self.running:
            iteration += 1
            if self.debug:
                print(f"\n--- Итерация {iteration} ---")

            jvg = self.store.get(current_doc_id)
            if not jvg:
                return {"status": "error", "error": f"Документ {current_doc_id} не найден"}

            fsm = FSMEngine(jvg, debug=self.debug)
            data = jvg.get("vectorograph", {})
            state = data.get("state", {})
            current_state = state.get("current", fsm.get_initial_state())

            self._log(3, "Текущее состояние", current_state)

            if current_state == "ЗАВЕРШЕНО":
                final_state = "ЗАВЕРШЕНО"
                print(f"✅ Агент завершил работу в состоянии {current_state}")
                break

            action_result, facts, next_state = self._execute_rules(jvg, current_state)

            if not next_state:
                transitions = fsm.get_available_transitions(current_state)
                if transitions:
                    next_state = transitions[0].get("to")
                else:
                    print(f"ℹ️ Нет доступных переходов из состояния {current_state}")
                    if not self.loop:
                        break
                    time.sleep(2)
                    continue

            self._log(6, "Выбран переход", f"{current_state} → {next_state}")

            state["current"] = next_state
            evolution = data.get("evolution", {})
            history_entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Агент: {current_state} → {next_state}"
            evolution["history"] = evolution.get("history", "") + "\n" + history_entry

            jvg["vectorograph"]["state"] = state
            jvg["vectorograph"]["evolution"] = evolution
            jvg = Identity.version(jvg, next_state)

            if action_result:
                history_entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Результат: {action_result.to_dict()}"
                jvg["vectorograph"]["evolution"]["history"] = jvg["vectorograph"]["evolution"].get("history", "") + "\n" + history_entry

            if facts:
                history_entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Факты: {facts}"
                jvg["vectorograph"]["evolution"]["history"] = jvg["vectorograph"]["evolution"].get("history", "") + "\n" + history_entry

            # Сохраняем обновлённый документ (обновляем текущий, не создаём новый)
            ok = self.store.update(current_doc_id, jvg)
            if not ok:
                return {"status": "error", "error": f"Не удалось обновить документ {current_doc_id}"}

            new_doc_id = current_doc_id

            self._log(17, "Документ обновлён", new_doc_id)

            EventBus.publish(f"agent.transition", {
                "doc_id": new_doc_id,
                "from_state": current_state,
                "to_state": next_state,
                "facts": facts
            })

            print(f"✅ Переход: {current_state} → {next_state}")

            current_doc_id = new_doc_id

            if not self.loop:
                break

            time.sleep(1)

        return {
            "status": "ok",
            "doc_id": current_doc_id,
            "final_state": final_state or state.get("current", "unknown"),
            "iterations": iteration
        }

    def stop(self):
        self.running = False
