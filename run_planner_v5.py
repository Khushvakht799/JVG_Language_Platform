"""
run_planner_v5.py — Запуск универсального когнитивного движка
"""

from jvg import PlannerV5, JVGStore

def main():
    store = JVGStore()
    doc_id = "GitAgent_20260711_114248_5bed76d1"

    jvg = store.get(doc_id)
    if not jvg:
        print(f"❌ Документ {doc_id} не найден")
        return

    print(f"✅ Документ найден: {doc_id}")

    planner = PlannerV5(store)
    
    # Устанавливаем цель высокого уровня
    planner.set_goal({"repository_synced": True})
    planner.max_iterations = 15

    result = planner.run(doc_id)

    print(f"\n📊 Результат:")
    print(f"  Статус: {result['status']}")
    print(f"  Итераций: {result.get('iterations', 0)}")
    if result.get('final_state'):
        print(f"  Финальное состояние:")
        pprint.pprint(result['final_state'])

if __name__ == "__main__":
    import pprint
    main()
