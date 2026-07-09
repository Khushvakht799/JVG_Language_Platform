"""
jvg/cli/doctor.py — Диагностика новой архитектуры
"""

from ..storage.store import JVGStore
from ..runtime.runtime import JVGRuntime

def doctor():
    print("🔍 JVG Doctor v2.0")
    print("=" * 50)
    
    # Проверяем хранилище
    try:
        store = JVGStore()
        items = store.list()
        print(f"✅ Хранилище: {len(items)} документов")
    except Exception as e:
        print(f"❌ Хранилище: {e}")
    
    # Проверяем Runtime
    try:
        runtime = JVGRuntime()
        print("✅ Runtime: работает")
    except Exception as e:
        print(f"❌ Runtime: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    doctor()
