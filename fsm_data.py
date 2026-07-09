"""
fsm_data.py — Пример FSM в JVG
"""

import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'jvg'))

from store import JVGStore

def main():
    jvg = {
        "vectorograph": {
            "meta": {
                "version": "1.0",
                "title": "FSM для перезапуска Explorer",
                "date": "2026-07-08",
                "author": "JVG",
                "status": "готово"
            },
            "entity": {
                "name": "Перезапуск Explorer",
                "type": "процесс",
                "purpose": "Автоматическое восстановление Проводника Windows"
            },
            "state_machine": {
                "initial": "ОЖИДАНИЕ",
                "states": ["ОЖИДАНИЕ", "ДИАГНОСТИКА", "ВЫПОЛНЕНИЕ", "ЗАВЕРШЕНО", "ОШИБКА"],
                "transitions": [
                    {"from": "ОЖИДАНИЕ", "to": "ДИАГНОСТИКА", "event": "system_unstable"},
                    {"from": "ДИАГНОСТИКА", "to": "ВЫПОЛНЕНИЕ", "event": "diagnostics_ok"},
                    {"from": "ДИАГНОСТИКА", "to": "ОШИБКА", "event": "diagnostics_failed"},
                    {"from": "ВЫПОЛНЕНИЕ", "to": "ЗАВЕРШЕНО", "event": "execution_success"},
                    {"from": "ВЫПОЛНЕНИЕ", "to": "ОШИБКА", "event": "execution_failed"}
                ],
                "rules": [
                    {"event": "system_unstable", "action": "run_diagnostics"},
                    {"event": "diagnostics_ok", "action": "restart_explorer"},
                    {"event": "diagnostics_failed", "action": "send_alert"},
                    {"event": "execution_success", "action": "send_notification"},
                    {"event": "execution_failed", "action": "send_alert"}
                ]
            },
            "state": {"current": "ОЖИДАНИЕ"},
            "actions": {"next_steps": ["Запустить процесс", "Отслеживать состояние"]},
            "evolution": {"history": "Создан как пример FSM"}
        }
    }

    store = JVGStore()
    doc_id = store.save(jvg)
    print(f"✅ Документ с FSM сохранён: {doc_id}")

if __name__ == "__main__":
    main()
