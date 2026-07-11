"""
test_git.py — Тест Git Executor
"""

from jvg import ActionExecutor

def main():
    print("📤 Тест Git Executor")
    
    # Проверяем статус
    result = ActionExecutor.execute(
        "run_git",
        {
            "command": "status",
            "repo_path": "."
        }
    )
    
    print(f"✅ Успешно: {result.success}")
    print(f"📝 Вывод:\n{result.stdout}")
    if result.error:
        print(f"❌ Ошибка: {result.error}")

if __name__ == "__main__":
    main()
