"""
jvg_runtime.py — Интегрированный Runtime
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional

from jvg import JVGStore, JVGRuntime
from jvg.config import STORAGE_DIR

class ActionExecutor:
    @staticmethod
    def execute(action: str, params: Dict[str, Any], doc_id: str) -> Dict[str, Any]:
        result = {"status": "ok", "action": action, "doc_id": doc_id}

        if action == "transition" and "to_state" in params:
            runtime = JVGRuntime(storage_dir=STORAGE_DIR)
            step_result = runtime.step(doc_id, params["to_state"], f"Автоматический переход по правилу")
            result.update(step_result)

        elif action == "run_powershell" and "command" in params:
            command = params["command"]
            print(f"   ⚡ Выполнение PowerShell: {command}")
            try:
                process = subprocess.run(
                    ["powershell", "-Command", command],
                    capture_output=True,
                    text=True,
                    shell=False,
                    timeout=30
                )
                result["stdout"] = process.stdout
                result["stderr"] = process.stderr
                result["returncode"] = process.returncode
                if process.returncode == 0:
                    print(f"   ✅ Команда выполнена успешно")
                else:
                    print(f"   ⚠️ Команда завершилась с кодом {process.returncode}")
            except subprocess.TimeoutExpired:
                result["status"] = "error"
                result["error"] = "Команда выполнялась слишком долго"
            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)

        elif action == "run_cmd" and "command" in params:
            command = params["command"]
            print(f"   ⚡ Выполнение CMD: {command}")
            try:
                process = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                result["stdout"] = process.stdout
                result["stderr"] = process.stderr
                result["returncode"] = process.returncode
                if process.returncode == 0:
                    print(f"   ✅ Команда выполнена успешно")
                else:
                    print(f"   ⚠️ Команда завершилась с кодом {process.returncode}")
            except subprocess.TimeoutExpired:
                result["status"] = "error"
                result["error"] = "Команда выполнялась слишком долго"
            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)

        elif action == "create_task" and "task_name" in params:
            task_name = params["task_name"]
            print(f"   📋 Создана задача: {task_name}")
            result["task"] = task_name

        elif action == "send_notification" and "message" in params:
            message = params["message"]
            print(f"   📧 Уведомление: {message}")
            result["message"] = message

        else:
            result["status"] = "error"
            result["error"] = f"Неизвестное действие: {action}"

        return result


class IntegratedRuntime:
    def __init__(self, debug: bool = False):
        self.store = JVGStore(storage_dir=STORAGE_DIR)
        self.runtime = JVGRuntime(storage_dir=STORAGE_DIR)
        self.debug = debug

    def step(self, doc_id: str, new_state: Optional[str] = None,
             action_result: Optional[str] = None) -> Dict[str, Any]:
        jvg = self.store.get(doc_id)
        if not jvg:
            return {"status": "error", "error": f"Документ {doc_id} не найден"}

        # Используем FSM из документа, если есть
        from fsm_engine import FSMEngine
        fsm = FSMEngine(jvg)
        current_state = jvg.get("vectorograph", {}).get("state", {}).get("current", fsm.get_initial_state())

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

        result = self.runtime.step(doc_id, new_state, action_result)
        if result.get("status") == "ok":
            result["available"] = fsm.get_available_transitions(new_state or current_state)

        return result

def test_integrated_runtime():
    print("🧪 Тест Integrated Runtime")
    print("=" * 50)

    store = JVGStore(storage_dir=STORAGE_DIR)
    integrated = IntegratedRuntime(debug=True)

    target_id = None
    for item in store.list():
        if 'Перезапуск' in item.get('title', ''):
            target_id = item['id']
            break

    if not target_id:
        print("❌ Документ не найден")
        return

    print(f"✅ Документ найден: {target_id}")

    jvg = store.get(target_id)
    current_state = jvg.get("vectorograph", {}).get("state", {}).get("current", "")
    print(f"📊 Текущее состояние: {current_state}")

    from fsm_engine import FSMEngine
    fsm = FSMEngine(jvg)
    available = fsm.get_available_transitions(current_state)
    print(f"📋 Доступные переходы: {available}")

    print("\n🔄 Выполнение шага...")
    result = integrated.step(target_id, "НЕСТАБИЛЬНО", "Активация правил")
    print(f"Результат: {result}")

if __name__ == "__main__":
    test_integrated_runtime()
