"""
demo_planner.py — Демонстрация Goal Planner
"""

from jvg import GoalPlanner

def main():
    planner = GoalPlanner()
    
    # Пример 1: Сервис не работает
    facts = {
        "http": {
            "status_code": 503,
            "success": False
        }
    }
    
    plan = planner.plan("Сервис должен быть доступен", facts)
    print("\n📋 План:")
    for step in plan:
        print(f"  Шаг {step['step']}: {step['action']} (агент: {step['agent']})")
        print(f"    Причина: {step['reason']}")
    
    evaluation = planner.evaluate_plan(plan)
    print(f"\n📊 Оценка плана:")
    print(f"  Шагов: {evaluation['total_steps']}")
    print(f"  Риск: {evaluation['total_risk']}/10")
    print(f"  Рекомендация: {evaluation['recommendation']}")

if __name__ == "__main__":
    main()
