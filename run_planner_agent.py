"""
run_planner_agent.py — Запуск агента с PlannerV2
"""

from jvg import PlannerV2, JVGStore

def main():
    store = JVGStore()
    doc_id = "GitAgent_20260711_114248_5bed76d1"

    # Получаем документ
    jvg = store.get(doc_id)
    if not jvg:
        print(f"❌ Документ {doc_id} не найден")
        return

    # Получаем последние факты из документа
    data = jvg.get("vectorograph", {})
    evolution = data.get("evolution", {})
    history = evolution.get("history", "")

    # Извлекаем последние факты из истории
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

    print("🧠 Запуск PlannerV2 для агента...")
    print(f"📊 Последние факты: {last_fact}")

    # Планировщик
    planner = PlannerV2(store)

    # Анализируем варианты
    actions = planner.analyze(last_fact or {})
    print(f"\n📋 Возможные действия:")
    for a in actions:
        print(f"  {a['action']} (скор: {a.get('score', 0):.2f}) — {a['reason']}")

    # Выбираем лучшее действие
    action = planner.choose_action(last_fact or {})
    if action:
        print(f"\n✅ Выбрано действие: {action['action']} (скор: {action.get('score', 0):.2f})")
        result = planner.execute_plan(last_fact or {}, doc_id)
        print(f"📝 Результат: {result}")
    else:
        print("ℹ️ Нет подходящих действий")

if __name__ == "__main__":
    main()
