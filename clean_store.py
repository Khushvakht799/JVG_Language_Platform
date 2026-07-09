"""
clean_store.py — Очистка хранилища (оставляем только последний документ)
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'jvg'))

from jvg import JVGStore

def main():
    store = JVGStore()
    items = store.list()
    
    # Находим последний документ с перезапуском
    last = None
    for item in items:
        if 'Перезапуск_Explorer' in item['id']:
            if not last or item['id'] > last['id']:
                last = item
    
    if not last:
        print("❌ Документы не найдены")
        return
    
    print(f"✅ Оставляем: {last['id']}")
    
    deleted = 0
    for item in items:
        if item['id'] != last['id'] and 'Перезапуск_Explorer' in item['id']:
            store.delete(item['id'])
            print(f"   🗑️ Удаляем: {item['id']}")
            deleted += 1
    
    print(f"\n✅ Удалено: {deleted} документов")
    print(f"✅ Осталось: {len(store.list())} документов")

if __name__ == "__main__":
    main()
