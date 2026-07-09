"""
store.py — Хранилище JVG (с rebuild_index)
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

class JVGStore:
    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            storage_dir = "jvg_store"
        self.storage_dir = storage_dir
        self.index_file = os.path.join(storage_dir, "index.json")
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_index(self) -> List[Dict[str, Any]]:
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_index(self, index: List[Dict[str, Any]]):
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def _generate_id(self, jvg: Dict[str, Any]) -> str:
        data = jvg.get("vectorograph", {})
        entity = data.get("entity", {})
        meta = data.get("meta", {})
        name = entity.get("name", meta.get("title", "unknown"))
        clean_name = "".join(c for c in name if c.isalnum() or c in " ._-")
        clean_name = clean_name.replace(" ", "_")
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_str = hashlib.md5(json.dumps(jvg, sort_keys=True).encode()).hexdigest()[:8]
        return f"{clean_name}_{date_str}_{hash_str}"

    def save(self, jvg: Dict[str, Any]) -> str:
        doc_id = self._generate_id(jvg)
        file_path = os.path.join(self.storage_dir, f"{doc_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(jvg, f, ensure_ascii=False, indent=2)
        index = self._load_index()
        data = jvg.get("vectorograph", {})
        meta = data.get("meta", {})
        entity = data.get("entity", {})
        index.append({
            "id": doc_id,
            "file": f"{doc_id}.json",
            "timestamp": datetime.now().isoformat(),
            "title": meta.get("title", "untitled"),
            "type": entity.get("type", "unknown")
        })
        self._save_index(index)
        return doc_id

    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        file_path = os.path.join(self.storage_dir, f"{doc_id}.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list(self) -> List[Dict[str, Any]]:
        return self._load_index()

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

    def delete(self, doc_id: str) -> bool:
        """Удаляет документ по ID."""
        file_path = os.path.join(self.storage_dir, f"{doc_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
        # Обновляем индекс
        index = self._load_index()
        new_index = [item for item in index if item.get("id") != doc_id]
        self._save_index(new_index)
        return True
