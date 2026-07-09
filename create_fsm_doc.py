"""
create_fsm_doc.py — Создание документа с State Machine
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
                "title": "State Machine Пример",
                "date": "2026-07-08",
                "author": "JVG",
                "status": "готово"
            },
            "entity": {
                "name": "Процесс с FSM",
                "type": "процесс",
                "purpose": "Демонстрация конечного автомата в JVG"
            },
            "state_machine": {
                "initial": "ОЖИДАНИЕ",
                "states": ["ОЖИДАНИЕ", "ПРОВЕРКА", "ВЫПОЛНЕНИЕ", "ЗАВЕРШЕНО"],
                "transitions": [
                    {"from": "ОЖИДАНИЕ", "to": "ПРОВЕРКА", "condition": "диагностика_пройдена", "action": "запустить_диагностику"},
                    {"from": "ПРОВЕРКА", "to": "ВЫПОЛНЕНИЕ", "condition": "ошибок_нет", "action": "запустить_процесс"},
                    {"from": "ВЫПОЛНЕНИЕ", "to": "ЗАВЕРШЕНО", "condition": "процесс_завершён", "action": "завершить_процесс"}
                ]
            },
            "state": {"current": "ОЖИДАНИЕ"},
            "actions": {"next_steps": ["Проверить FSM"]},
            "evolution": {"history": "Создан как демонстрация FSM в JVG"}
        }
    }

    store = JVGStore()
    doc_id = store.save(jvg)
    print(f"✅ Документ с FSM сохранён: {doc_id}")

if __name__ == "__main__":
    main()
