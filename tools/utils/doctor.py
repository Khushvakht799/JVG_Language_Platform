"""
doctor.py — Диагностика системы JVG
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

def check_imports():
    """Проверяет импорты."""
    print("🔍 Проверка импортов...")
    try:
        from jvg import JVGStore, JVGVectorizer, JVGRankingEngine, JVGCompiler
        print("  ✅ Все модули импортируются")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка импорта: {e}")
        return False

def check_storage():
    """Проверяет хранилище."""
    print("📁 Проверка хранилища...")
    try:
        from jvg import JVGStore
        store = JVGStore()
        items = store.list()
        print(f"  ✅ Хранилище работает, документов: {len(items)}")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка хранилища: {e}")
        return False

def check_chroma():
    """Проверяет ChromaDB."""
    print("🧠 Проверка ChromaDB...")
    try:
        from jvg import JVGVectorizer
        vectorizer = JVGVectorizer()
        # Просто проверяем, что коллекция есть
        result = vectorizer.search("test", top_k=1)
        print("  ✅ ChromaDB работает")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка ChromaDB: {e}")
        return False

def check_api():
    """Проверяет API."""
    print("🌐 Проверка API...")
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=3)
        if response.status_code == 200:
            print("  ✅ API работает")
            return True
        else:
            print(f"  ⚠️ API отвечает с кодом {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ⚠️ API не запущен (localhost:8000)")
        return False
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

def main():
    print("=" * 50)
    print("JVG Doctor — Диагностика системы")
    print("=" * 50)

    results = {
        "imports": check_imports(),
        "storage": check_storage(),
        "chroma": check_chroma(),
        "api": check_api()
    }

    print("\n" + "=" * 50)
    print("ИТОГ:")
    for name, status in results.items():
        print(f"  {name}: {'✅' if status else '❌'}")

    if all(results.values()):
        print("\n✅ Система полностью здорова!")
    else:
        print("\n⚠️ Есть проблемы, требующие внимания.")

if __name__ == "__main__":
    main()
