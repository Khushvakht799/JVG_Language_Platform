"""
l2_memory.py — Слой памяти L2
"""

import os
import sys
from typing import Dict, Any, List, Optional

from .store import JVGStore
from .vectorizer import JVGVectorizer

class L2Memory:
    def __init__(self, storage_dir: str = "jvg_store", vector_db_path: str = "jvg_chroma_db"):
        self.store = JVGStore(storage_dir=storage_dir)
        self.vectorizer = JVGVectorizer(db_path=vector_db_path)

    def save(self, jvg: Dict[str, Any]) -> str:
        doc_id = self.store.save(jvg)
        self.vectorizer.vectorize(jvg, doc_id)
        return doc_id

    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get(doc_id)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return self.vectorizer.search(query, top_k=top_k)

    def list(self) -> List[Dict[str, Any]]:
        return self.store.list()

    def delete(self, doc_id: str) -> bool:
        return True
