"""
jvg/cli/tools.py — CLI с режимом цикла
"""

import sys
from typing import Optional
from ..storage.store import JVGStore
from ..runtime.executor import JVGExecutor

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

def run_doc(query: str, debug: bool = False, loop: bool = False):
    store = JVGStore()
    doc_id = resolve_doc_id(store, query)
    if not doc_id:
        print(f"❌ Документ не найден: {query}")
        return

    executor = JVGExecutor(debug=debug, loop=loop)
    result = executor.execute(doc_id)
    if result.get("status") == "ok":
        print(f"✅ Автоматический переход: {result['old_state']} → {result['new_state']}")
        print(f"   Доступно: {result.get('available', [])}")
    elif result.get("status") == "idle":
        print(f"ℹ️ Документ в состоянии {result['state']}, нет доступных переходов")
    else:
        print(f"❌ Ошибка: {result.get('error')}")

def main():
    if len(sys.argv) < 2:
        print("""
JVG CLI v2.0

Использование:
    python -m jvg.cli.tools list
    python -m jvg.cli.tools run <query> [--debug] [--loop]
    
Примеры:
    python -m jvg.cli.tools run Монитор --loop
""")
        return

    cmd = sys.argv[1]
    if cmd == "list":
        list_docs()
    elif cmd == "run" and len(sys.argv) > 2:
        debug = "--debug" in sys.argv
        loop = "--loop" in sys.argv
        run_doc(sys.argv[2], debug, loop)
    else:
        print(f"❌ Неизвестная команда: {cmd}")

if __name__ == "__main__":
    main()
