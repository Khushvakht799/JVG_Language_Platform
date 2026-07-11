"""
test_security_v2.py — Тест Security Engine V2
"""

from jvg import SecurityEngineV2

def main():
    engine = SecurityEngineV2()
    
    # Тест 1: Неизвестный исполнитель
    print("=== Тест 1: Неизвестный исполнитель ===")
    result = engine.check("unknown_action", {})
    print(f"Действие: unknown_action")
    print(f"Решение: {result['final_decision']}")
    print(f"Сообщение: {result['message']}\n")
    
    # Тест 2: Известный, но не зарегистрированный в политике
    print("=== Тест 2: Известный, без политики ===")
    result = engine.check("run_git", {"command": "status"})
    print(f"Действие: run_git")
    print(f"Существует: {result['executor_exists']}")
    print(f"Политика: {result['policy_allowed']}")
    print(f"Риск: {result['risk_score']}")
    print(f"Решение: {result['final_decision']}")
    print(f"Сообщение: {result['message']}\n")
    
    # Тест 3: Запрещённый паттерн
    print("=== Тест 3: Запрещённый паттерн ===")
    result = engine.check("run_cmd", {"command": "format C:"})
    print(f"Действие: run_cmd")
    print(f"Решение: {result['final_decision']}")
    print(f"Сообщение: {result['message']}")
    print(f"Паттерн: {result['blocked_pattern']}")

if __name__ == "__main__":
    main()
