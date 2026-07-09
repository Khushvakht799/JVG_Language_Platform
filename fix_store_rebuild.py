"""
fix_store_rebuild.py — Добавляет метод rebuild_index в JVGStore
"""

import os
import json
import sys

STORE_PATH = "jvg/store.py"

with open(STORE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Проверяем, есть ли уже метод rebuild_index
if "def rebuild_index" in content:
    print("ℹ️ Метод rebuild_index уже существует")
    sys.exit(0)

# Находим конец класса (последний метод)
import re
pattern = r'(\s+def delete\([^)]+\):[^\n]*\n(?:\s+.*\n)*?)'
match = re.search(pattern, content)
if match:
    # Вставляем метод перед delete
    new_method = '''
    def rebuild_index(self):
        """Перестраивает индекс из реальных файлов."""
        index = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json') and filename != 'index.json':
                file_path = os.path.join(self.storage_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        jvg = json.load(f)
                    data = jvg.get("vectorograph", {})
                    meta = data.get("meta", {})
                    entity = data.get("entity", {})
                    doc_id = filename.replace('.json', '')
                    index.append({
                        "id": doc_id,
                        "file": filename,
                        "timestamp": meta.get("date", ""),
                        "title": meta.get("title", "без названия"),
                        "type": entity.get("type", "unknown")
                    })
                except Exception as e:
                    print(f"⚠️ Ошибка чтения {filename}: {e}")
        
        self._save_index(index)
        print(f"✅ Индекс перестроен. Найдено документов: {len(index)}")
'''
    # Вставляем перед delete
    content = content.replace(match.group(0), new_method + "\n" + match.group(0))
    
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Метод rebuild_index добавлен в JVGStore")
else:
    print("❌ Не найден метод delete")
