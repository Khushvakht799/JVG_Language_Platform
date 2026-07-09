"""
jvg/storage/store.py — Хранилище JVG с поиском
"""

import json
import hashlib
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..core.config import Config

class JVGStore:
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir or Config.STORAGE_PATH)
        self.storage_dir.mkdir(exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self._ensure_index()

    def _ensure_index(self):
        if not self.index_file.exists():
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)

    def _load_index(self) -> List[Dict[str, Any]]:
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_index(self, index: List[Dict[str, Any]]):
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)

    def _generate_id(self, jvg: Dict[str, Any]) -> str:
        name = jvg.get("vectorograph", {}).get("entity", {}).get("name", "unknown")
        clean = "".join(c for c in name if c.isalnum() or c in " ._-").replace(" ", "_")
        hash_suffix = hashlib.md5(json.dumps(jvg, sort_keys=True).encode()).hexdigest()[:8]
        return f"{clean}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash_suffix}"

    def _extract_logical_name(self, doc_id: str) -> str:
        parts = doc_id.split('_')
        if len(parts) >= 3:
            return '_'.join(parts[:-2])
        return doc_id

    def create(self, jvg: Dict[str, Any]) -> str:
        doc_id = self._generate_id(jvg)
        return self._save_document(doc_id, jvg)

    def update(self, doc_id: str, jvg: Dict[str, Any]) -> bool:
        if not self.get(doc_id):
            return False
        self._save_document(doc_id, jvg, overwrite=True)
        return True

    def _save_document(self, doc_id: str, jvg: Dict[str, Any], overwrite: bool = False) -> str:
        file_path = self.storage_dir / f"{doc_id}.json"
        if not overwrite and file_path.exists():
            doc_id = self._generate_id(jvg)
            file_path = self.storage_dir / f"{doc_id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(jvg, f, indent=2)
        
        index = self._load_index()
        new_index = [item for item in index if item.get("id") != doc_id]
        
        new_entry = {
            "id": doc_id,
            "logical_name": self._extract_logical_name(doc_id),
            "file": f"{doc_id}.json",
            "timestamp": datetime.now().isoformat(),
            "title": jvg.get("vectorograph", {}).get("meta", {}).get("title", ""),
            "type": jvg.get("vectorograph", {}).get("entity", {}).get("type", "")
        }
        new_index.append(new_entry)
        self._save_index(new_index)
        return doc_id

    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        path = self.storage_dir / f"{doc_id}.json"
        if not path.exists():
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def find_by_name(self, logical_name: str) -> Optional[str]:
        index = self._load_index()
        versions = []
        for item in index:
            if item.get("logical_name") == logical_name:
                versions.append(item)
        if not versions:
            return None
        versions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return versions[0].get("id")

    def find(self, query: str) -> List[Dict[str, Any]]:
        """
        Универсальный поиск:
        - по полному ID
        - по началу ID
        - по логическому имени
        - по названию (title)
        - по типу
        """
        index = self._load_index()
        results = []
        query_lower = query.lower()
        
        for item in index:
            # По ID
            if query == item.get("id"):
                results.append(item)
                continue
            # По логическому имени
            if query == item.get("logical_name"):
                results.append(item)
                continue
            # По началу ID
            if item.get("id", "").startswith(query):
                results.append(item)
                continue
            # По названию (частичное совпадение)
            title = item.get("title", "").lower()
            if query_lower in title:
                results.append(item)
                continue
            # По логическому имени (частичное)
            logical = item.get("logical_name", "").lower()
            if query_lower in logical:
                results.append(item)
                continue
        
        return results

    def list(self) -> List[Dict[str, Any]]:
        return self._load_index()

    def delete(self, doc_id: str) -> bool:
        path = self.storage_dir / f"{doc_id}.json"
        if path.exists():
            os.remove(path)
        index = self._load_index()
        new_index = [item for item in index if item.get("id") != doc_id]
        self._save_index(new_index)
        return True

    def rebuild_index(self):
        index = []
        for file in self.storage_dir.glob("*.json"):
            if file.name == "index.json":
                continue
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    jvg = json.load(f)
                data = jvg.get("vectorograph", {})
                meta = data.get("meta", {})
                entity = data.get("entity", {})
                doc_id = file.stem
                index.append({
                    "id": doc_id,
                    "logical_name": self._extract_logical_name(doc_id),
                    "file": file.name,
                    "timestamp": meta.get("date", ""),
                    "title": meta.get("title", "без названия"),
                    "type": entity.get("type", "unknown")
                })
            except Exception as e:
                print(f"⚠️ Ошибка чтения {file.name}: {e}")
        self._save_index(index)
        print(f"✅ Индекс перестроен. Найдено документов: {len(index)}")
