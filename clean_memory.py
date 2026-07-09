"""
clean_memory.py — Удаление мусорных документов из хранилища
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'jvg'))

from store import JVGStore

def main():
    store = JVGStore()
    
    # Список ID, которые нужно сохранить
    keep_ids = [
        'Перезапуск_Explorer_20260708_133906_aba12fd4',  # Рабочий пример
    ]
    
    items = store.list()
    deleted_count = 0
    
    for item in items:
        doc_id = item.get('id', '')
        title = item.get('title', '')
        
        # Пропускаем если нужно сохранить
        if doc_id in keep_ids:
            print(f"✅ Сохраняем: {doc_id} ({title})")
            continue
        
        # Удаляем всё остальное
        print(f"🗑️ Удаляем: {doc_id} ({title})")
        store.delete(doc_id)
        deleted_count += 1
    
    print(f"\n✅ Очистка завершена. Удалено: {deleted_count}")

if __name__ == "__main__":
    main()
