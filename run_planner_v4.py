"""
run_planner_v4.py — Запуск итеративного планировщика (с диагностикой)
"""

from jvg import PlannerV4, JVGStore
import pprint

def main():
    store = JVGStore()
    doc_id = "GitAgent_20260711_114248_5bed76d1"

    # Проверяем, что документ существует
    jvg = store.get(doc_id)
    if not jvg:
        print(f"❌ Документ {doc_id} не найден")
        return

    print(f"✅ Документ найден: {doc_id}")

    # Создаём планировщик
    planner = PlannerV4(store)
    planner.set_goal({"clean_repo": True})
    planner.max_iterations = 15

    # Добавляем диагностику: выводим полные факты перед запуском
    data = jvg.get("vectorograph", {})
    evolution = data.get("evolution", {})
    history = evolution.get("history", "")

    if history:
        lines = history.strip().split("\n")
        for line in reversed(lines):
            if "Факты:" in line:
                try:
                    fact_part = line.split("Факты:")[1].strip()
                    print("📊 Начальные факты:")
                    pprint.pprint(eval(fact_part))
                except:
                    pass
                break

    # Запускаем итеративное выполнение
    result = planner.run(doc_id)

    print(f"\n📊 Результат:")
    print(f"  Статус: {result['status']}")
    print(f"  Итераций: {result.get('iterations', 0)}")
    if result.get('final_state'):
        print(f"  Финальное состояние:")
        pprint.pprint(result['final_state'])

if __name__ == "__main__":
    main()
