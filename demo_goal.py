"""
demo_goal.py — Демонстрация Goal Engine
"""

from jvg import JVGStore, GoalEngine, EventBus

def on_goal_executed(data):
    print(f"✅ Цель выполнена: {data}")

# Регистрируем обработчик события
EventBus.subscribe("goal.restore_service", on_goal_executed)

# Создаём Goal Engine
goal_engine = GoalEngine()

# Регистрируем цель
goal_engine.register_goal(
    goal_id="restore_service",
    condition="fact.http.status_code != 200",
    action="run_repair",
    target_state="РАБОТАЕТ"
)

# Демонстрационные факты
facts = {
    "http": {
        "status_code": 503,
        "success": False
    }
}

print("\n📊 Факты:")
print(facts)

# Проверяем цели
triggered = goal_engine.evaluate(facts)
print(f"\n🎯 Сработавшие цели: {triggered}")

# Выполняем цели
if triggered:
    goal_engine.execute_goals(triggered, "demo_doc")
