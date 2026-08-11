"""
run_planner_v11.py — Запуск когнитивного ядра с Reasoner и Learning
"""

from jvg import PlannerV11, JVGStore
import pprint

def main():
    store = JVGStore()
    doc_id = "GitAgent_20260711_114248_5bed76d1"

    jvg = store.get(doc_id)
    if not jvg:
        print(f"❌ Документ {doc_id} не найден")
        return

    print(f"✅ Документ найден: {doc_id}")

    planner = PlannerV11(store)
    
    planner.set_goal({
        "is_clean": True,
        "is_ahead": False,
        "is_behind": False
    })
    planner.max_iterations = 10

    result = planner.run(doc_id)

    print(f"\n📊 Результат:")
    print(f"  Статус: {result['status']}")
    print(f"  Итераций: {result.get('iterations', 0)}")
    if result.get('final_state'):
        print(f"  Финальное состояние:")
        pprint.pprint(result['final_state'])

if __name__ == "__main__":
    main()
