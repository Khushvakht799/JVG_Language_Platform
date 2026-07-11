"""
run_agent.py — Запуск Git-агента через AgentRunner
"""

from jvg import AgentRunner

def main():
    runner = AgentRunner(debug=True, loop=True)
    result = runner.run("GitAgent_20260711_114248_5bed76d1")
    
    print(f"\n📊 Результат:")
    print(f"  Статус: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'ok':
        print(f"  Финальное состояние: {result.get('final_state', 'неизвестно')}")
        print(f"  Итераций: {result.get('iterations', 0)}")
        print(f"  ID документа: {result.get('doc_id', 'неизвестен')}")
    else:
        print(f"  Ошибка: {result.get('error', 'неизвестная ошибка')}")

if __name__ == "__main__":
    main()
