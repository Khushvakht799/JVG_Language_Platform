"""
scripts/reset_state.py — Сброс состояния документа по логическому имени
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from jvg import JVGStore

def main():
    store = JVGStore()
    
    # Ищем документ по логическому имени
    doc_id = store.find_by_name('Перезапуск_Explorer')
    if not doc_id:
        # Пробуем найти по названию
        results = store.find('Перезапуск')
        if results:
            doc_id = results[0].get('id')
            print(f"🔍 Найдено по названию: {doc_id}")
        else:
            print("❌ Документ не найден")
            return
    
    print(f"✅ Документ найден: {doc_id}")
    
    doc = store.get(doc_id)
    if not doc:
        print("❌ Ошибка загрузки документа")
        return
    
    if "vectorograph" not in doc:
        doc["vectorograph"] = {}
    if "state" not in doc["vectorograph"]:
        doc["vectorograph"]["state"] = {}
    
    doc["vectorograph"]["state"]["current"] = "ОЖИДАНИЕ"
    
    store.update(doc_id, doc)
    print("✅ Состояние сброшено в ОЖИДАНИЕ")

if __name__ == "__main__":
    main()
