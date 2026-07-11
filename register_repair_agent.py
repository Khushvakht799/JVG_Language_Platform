"""
register_repair_agent.py — Регистрация агента-ремонт
"""

from jvg import JVGStore
from jvg.events.event_bus import EventBus

def on_http_failure(data):
    print(f"🔧 Агент-ремонт: получено событие {data}")
    store = JVGStore()
    
    repair_doc = {
        "vectorograph": {
            "meta": {"title": "Ремонт"},
            "entity": {"name": "Ремонт", "type": "процесс"},
            "state": {"current": "ОЖИДАНИЕ"},
            "state_machine": {
                "initial": "ОЖИДАНИЕ",
                "states": ["ОЖИДАНИЕ", "ВЫПОЛНЕНИЕ", "ЗАВЕРШЕНО"],
                "transitions": [
                    {"from": "ОЖИДАНИЕ", "to": "ВЫПОЛНЕНИЕ"},
                    {"from": "ВЫПОЛНЕНИЕ", "to": "ЗАВЕРШЕНО"}
                ],
                "rules": [
                    {
                        "condition": "state == ВЫПОЛНЕНИЕ",
                        "action": "run_powershell",
                        "action_params": {"command": "Write-Host '🔧 Выполняем ремонт...'"}
                    },
                    {
                        "condition": "state == ЗАВЕРШЕНО",
                        "action": "run_powershell",
                        "action_params": {"command": "Write-Host '✅ Ремонт завершён'"}
                    }
                ]
            }
        }
    }
    
    repair_id = store.create(repair_doc)
    print(f"   📄 Создан документ ремонта: {repair_id}")

# Подписываемся на событие перехода в НЕ_РАБОТАЕТ
EventBus.subscribe("transition.ПРОВЕРКА_НЕ_РАБОТАЕТ", on_http_failure)

print("✅ Агент-ремонт зарегистрирован")
