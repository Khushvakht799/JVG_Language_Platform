"""
jvg/cli/tools.py — CLI с универсальным поиском (исправленный)
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
    """Находит документ по запросу."""
    results = store.find(query)
    if not results:
        return None
    if len(results) == 1:
        return results[0].get("id")
    # Если несколько — показываем варианты
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
    
    executor = JVGExecutor(debug=debug)
    result = executor.execute(doc_id)
    if result["status"] == "ok":
        available = result.get('available', [])
        print(f"✅ Автоматический переход: {result['old_state']} → {result['new_state']}")
        print(f"   Доступно: {available}")
    elif result["status"] == "idle":
        states = result.get('states', [])
        print(f"ℹ️ Документ в состоянии {result['state']}, нет доступных переходов")
        if debug:
            print(f"   Все состояния: {states}")
    else:
        print(f"❌ Ошибка: {result.get('error')}")

def main():
    if len(sys.argv) < 2:
        print("""
JVG CLI v2.0

Использование:
    python -m jvg.cli.tools list
    python -m jvg.cli.tools run <query> [--debug]
    
Поиск работает по:
    - полному ID
    - логическому имени
    - части названия
    - части ID
    
Примеры:
    python -m jvg.cli.tools run Перезапуск
    python -m jvg.cli.tools run Explorer
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
