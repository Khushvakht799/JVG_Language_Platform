"""
purge.py — Полная очистка JVG Platform
"""

import sys
import os
import json
import shutil
import chromadb
from chromadb.config import Settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'jvg'))

from store import JVGStore

def main():
    print("🗑️ JVG Platform — Полная очистка")
    print("=" * 50)
    
    # 1. Удаляем JSON-документы и индекс
    print("📁 Очистка хранилища...")
    store = JVGStore()
    items = store.list()
    doc_count = len(items)
    for item in items:
        doc_id = item.get('id', '')
        store.delete(doc_id)
    print(f"   Удалено документов: {doc_count}")
    
    # 2. Очищаем папку хранилища (полностью)
    print("🗑️ Удаление папки хранилища...")
    store_path = store.storage_dir
    if os.path.exists(store_path):
        shutil.rmtree(store_path)
        print(f"   Удалена папка: {store_path}")
    
    # 3. Очищаем Chroma DB
    print("🧠 Очистка Chroma DB...")
    try:
        chroma_path = "jvg_chroma_db"
        if os.path.exists(chroma_path):
            shutil.rmtree(chroma_path)
            print(f"   Удалена папка Chroma: {chroma_path}")
    except Exception as e:
        print(f"   ⚠️ Ошибка очистки Chroma: {e}")
    
    # 4. Пересоздаём хранилище
    print("📁 Пересоздание хранилища...")
    store._ensure_storage()
    print("   Хранилище создано заново")
    
    # 5. Проверяем результат
    print("\n✅ Очистка завершена!")
    print(f"   Документов: {len(store.list())}")
    print("   Индекс: пуст")
    print("   Chroma: очищена")
    print("\n💡 Платформа готова к новой базе знаний.")

if __name__ == "__main__":
    main()
