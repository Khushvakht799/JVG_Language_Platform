"""
run_system.py — Полная система с автоматическим запуском ремонта
"""

from jvg import JVGStore, GoalEngine, EventBus, JVGExecutor

def on_http_failure(data):
    print(f"🔧 Обработчик ремонта: получено событие {data}")
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
    
    # Автоматически запускаем документ ремонта
    print(f"   🚀 Запуск документа ремонта: {repair_id}")
    executor = JVGExecutor(debug=True, loop=False)
    result = executor.execute(repair_id)
    print(f"   ✅ Результат ремонта: {result.get('new_state', 'unknown')}")
    
    # После завершения ремонта отправляем событие
    EventBus.publish("repair.success", {
        "doc_id": repair_id,
        "result": result
    })

def on_repair_success(data):
    print(f"🔁 Ремонт успешен, монитор продолжает работу: {data}")

def on_goal_restore(data):
    print(f"🎯 Цель restore_service выполнена: {data}")

def main():
    EventBus.subscribe("goal.restore_service", on_goal_restore)
    EventBus.subscribe("transition.ПРОВЕРКА_НЕ_РАБОТАЕТ", on_http_failure)
    EventBus.subscribe("repair.success", on_repair_success)

    goal_engine = GoalEngine()
    goal_engine.register_goal(
        goal_id="restore_service",
        condition="fact.http.status_code != 200",
        action="run_repair",
        target_state="РАБОТАЕТ"
    )

    print("\n" + "="*50)
    print("🚀 Запуск полной системы с замкнутым циклом")
    print("="*50 + "\n")

    store = JVGStore()
    doc_id = None
    for item in store.list():
        if "Монитор с условиями" in item.get("title", ""):
            doc_id = item.get("id")
            break

    if not doc_id:
        print("❌ Документ 'Монитор с условиями' не найден")
        return

    print(f"✅ Найден документ: {doc_id}")

    executor = JVGExecutor(debug=True, loop=True)
    executor.execute(doc_id)

if __name__ == "__main__":
    main()
