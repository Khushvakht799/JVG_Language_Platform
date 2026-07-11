"""
run_planner_v3.py — Запуск PlannerV3 с целью
"""

from jvg import PlannerV3, JVGStore, WorldModel

def main():
    store = JVGStore()
    doc_id = "GitAgent_20260711_114248_5bed76d1"

    # Получаем документ
    jvg = store.get(doc_id)
    if not jvg:
        print(f"❌ Документ {doc_id} не найден")
        return

    # Получаем факты
    data = jvg.get("vectorograph", {})
    evolution = data.get("evolution", {})
    history = evolution.get("history", "")

    last_fact = None
    if history:
        lines = history.strip().split("\n")
        for line in reversed(lines):
            if "Факты:" in line:
                try:
                    fact_part = line.split("Факты:")[1].strip()
                    last_fact = eval(fact_part)
                except:
                    pass
                break

    print("🧠 Запуск PlannerV3...")
    print(f"📊 Текущие факты: {last_fact}")

    # Создаём планировщик с целью
    planner = PlannerV3(store)
    planner.set_goal({"clean_repo": True})

    # Анализируем и выполняем план
    plan = planner.choose_plan(last_fact or {})
    if plan:
        print(f"\n✅ План выбран: {plan['action']} (стоимость: {plan.get('cost', 0)})")
        result = planner.execute_plan(last_fact or {}, doc_id)
        print(f"📝 Результат: {result}")
    else:
        print("ℹ️ Нет плана для достижения цели")

if __name__ == "__main__":
    main()
