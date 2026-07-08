"""
store.py — Хранилище JVG (с единым конфигом)
"""

import json
import hashlib
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Добавляем путь к корню проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
from config import JVG_STORE_PATH

class JVGStore:
    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            storage_dir = str(JVG_STORE_PATH)
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
        index.append({
            "id": doc_id,
            "file": f"{doc_id}.json",
            "timestamp": datetime.now().isoformat(),
            "title": jvg.get("vectorograph", {}).get("meta", {}).get("title", "untitled"),
            "type": jvg.get("vectorograph", {}).get("entity", {}).get("type", "unknown")
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

    def delete(self, doc_id: str) -> bool:
        # TODO: удаление
        return True
