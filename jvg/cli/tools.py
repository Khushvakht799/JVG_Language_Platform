"""
jvg/cli/tools.py — CLI с AgentRunner вместо старого исполнителя
"""

import sys
from typing import Optional
from ..storage.store import JVGStore
from ..agents.agent_runner import AgentRunner

def list_docs():
    store = JVGStore()
    items = store.list()
    if not items:
        print("  (пусто)")
        return
    for i, item in enumerate(items, 1):
        logical = item.get('logical_name', 'unknown')
        print(f"  {i}. {item.get('title', 'без названия')} ({item.get('type', 'unknown')}) — {logical}")

def resolve_doc_id(store: JVGStore, query: str) -> Optional[str]:
    results = store.find(query)
    if not results:
        return None
    if len(results) == 1:
        return results[0].get("id")
    print(f"🔍 Найдено {len(results)} документов по запросу '{query}':")
    for i, item in enumerate(results, 1):
        print(f"  {i}. {item.get('title', 'без названия')} ({item.get('logical_name', 'unknown')})")
    return None

def run_doc(query: str, debug: bool = False):
    store = JVGStore()
    doc_id = resolve_doc_id(store, query)
    if not doc_id:
        print(f"❌ Документ не найден: {query}")
        return

    # Используем AgentRunner вместо старого исполнителя
    runner = AgentRunner(debug=debug, loop=False)
    result = runner.run(doc_id)
    
    if result.get("status") == "ok":
        print(f"✅ Агент завершил работу")
        print(f"   Состояние: {result.get('final_state', 'unknown')}")
        print(f"   Итераций: {result.get('iterations', 0)}")
        print(f"   ID: {result.get('doc_id', 'unknown')}")
    else:
        print(f"❌ Ошибка: {result.get('error', 'неизвестная ошибка')}")

def main():
    if len(sys.argv) < 2:
        print("""
JVG CLI v2.0

Использование:
    python -m jvg.cli.tools list
    python -m jvg.cli.tools run <query> [--debug]
    
Примеры:
    python -m jvg.cli.tools run Перезапуск
    python -m jvg.cli.tools run Explorer --debug
""")
        return

    cmd = sys.argv[1]
    if cmd == "list":
        list_docs()
    elif cmd == "run" and len(sys.argv) > 2:
        debug = "--debug" in sys.argv
        run_doc(sys.argv[2], debug)
    else:
        print(f"❌ Неизвестная команда: {cmd}")

if __name__ == "__main__":
    main()
