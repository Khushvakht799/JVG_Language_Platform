"""
create_restart_doc.py — Создание документа с правилом перезапуска Explorer
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
                "title": "Автоматический перезапуск Проводника Windows",
                "date": "2026-07-08",
                "author": "JVG",
                "status": "готово"
            },
            "entity": {
                "name": "Перезапуск Explorer",
                "type": "процесс",
                "purpose": "Автоматическое восстановление Проводника Windows"
            },
            "context": {
                "origin": "Демонстрация Action Executor",
                "environment": "Windows 11",
                "dependencies": ["PowerShell", "CMD"]
            },
            "state": {
                "current": "ОЖИДАНИЕ",
                "problems": [],
                "risks": ["Потеря данных при принудительном завершении"]
            },
            "rules": [
                {
                    "condition": "state == НЕСТАБИЛЬНО",
                    "action": "run_cmd",
                    "action_params": {
                        "command": "taskkill /f /im explorer.exe && start explorer.exe"
                    }
                },
                {
                    "condition": "state == НЕСТАБИЛЬНО",
                    "action": "run_powershell",
                    "action_params": {
                        "command": "Write-Host 'Проводник перезапущен JVG'"
                    }
                }
            ],
            "triggers": [
                {
                    "event": "system_unstable",
                    "from": "ОЖИДАНИЕ",
                    "to": "НЕСТАБИЛЬНО",
                    "action": "запустить_восстановление"
                }
            ],
            "actions": {
                "next_steps": ["Перевести документ в состояние НЕСТАБИЛЬНО"],
                "required_resources": ["Права администратора"]
            },
            "evolution": {
                "history": "Создан как демонстрационный пример",
                "future_versions": ["Добавить проверку перезапуска"]
            }
        }
    }

    store = JVGStore()
    doc_id = store.save(jvg)
    print(f"✅ Документ сохранён: {doc_id}")

if __name__ == "__main__":
    main()
