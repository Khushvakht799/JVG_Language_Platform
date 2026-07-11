"""
run_planner_v8.py — Запуск A* планировщика с диагностикой
"""

from jvg import PlannerV8, JVGStore
import pprint

def main():
    store = JVGStore()
    doc_id = "GitAgent_20260711_114248_5bed76d1"

    jvg = store.get(doc_id)
    if not jvg:
        print(f"❌ Документ {doc_id} не найден")
        return

    print(f"✅ Документ найден: {doc_id}")

    # Проверяем текущее состояние Git
    print("\n📊 Текущее состояние Git:")
    data = jvg.get("vectorograph", {})
    evolution = data.get("evolution", {})
    history = evolution.get("history", "")
    if history:
        lines = history.strip().split("\n")
        for line in reversed(lines):
            if "Факты:" in line:
                try:
                    fact_part = line.split("Факты:")[1].strip()
                    pprint.pprint(eval(fact_part).get("git", {}))
                    break
                except:
                    pass

    planner = PlannerV8(store)
    
    planner.set_goal({
        "is_clean": True,
        "is_ahead": False,
        "is_behind": False
    })
    planner.max_plan_length = 10

    # Включаем диагностику в PlannerV8
    print("\n🧠 Запуск A* планировщика (с диагностикой)...")
    result = planner.run(doc_id)

    print(f"\n📊 Результат:")
    print(f"  Статус: {result['status']}")
    print(f"  Длина плана: {result.get('plan_length', 0)}")
    if result.get('final_state'):
        print(f"  Финальное состояние:")
        pprint.pprint(result['final_state'])

if __name__ == "__main__":
    main()
