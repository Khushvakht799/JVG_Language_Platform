"""
run_planner_v7.py — Запуск поиска плана
"""

from jvg import PlannerV7, JVGStore
import pprint

def main():
    store = JVGStore()
    doc_id = "GitAgent_20260711_114248_5bed76d1"

    jvg = store.get(doc_id)
    if not jvg:
        print(f"❌ Документ {doc_id} не найден")
        return

    print(f"✅ Документ найден: {doc_id}")

    planner = PlannerV7(store)
    
    # Устанавливаем целевое состояние
    planner.set_goal({
        "clean": True,
        "ahead": False,
        "behind": False
    })
    planner.max_plan_length = 10

    result = planner.run(doc_id)

    print(f"\n📊 Результат:")
    print(f"  Статус: {result['status']}")
    print(f"  Длина плана: {result.get('plan_length', 0)}")
    if result.get('final_state'):
        print(f"  Финальное состояние:")
        pprint.pprint(result['final_state'])

if __name__ == "__main__":
    main()
