"""
vectorizer.py — Векторизатор JVG (с единым конфигом)
"""

import os
import sys
from typing import Dict, Any, List, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
from config import CHROMA_DB_PATH, MODEL_NAME

class JVGVectorizer:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(CHROMA_DB_PATH)
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))
        self.model = SentenceTransformer(MODEL_NAME)
        self.collection_name = "jvg_vectors"
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.collection = self.client.get_collection(self.collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

    def _get_text_for_embedding(self, jvg: Dict[str, Any]) -> str:
        data = jvg.get("vectorograph", {})
        entity = data.get("entity", {})
        context = data.get("context", {})
        parts = [entity.get("name", ""), entity.get("purpose", ""), context.get("origin", "")]
        return " ".join(parts).strip() or "неизвестно"

    def vectorize(self, jvg: Dict[str, Any], doc_id: str) -> List[float]:
        text = self._get_text_for_embedding(jvg)
        vector = self.model.encode(text, normalize_embeddings=True).tolist()
        data = jvg.get("vectorograph", {})
        meta = data.get("meta", {})
        entity = data.get("entity", {})
        self.collection.add(
            ids=[doc_id],
            embeddings=[vector],
            metadatas=[{
                "title": meta.get("title", ""),
                "type": entity.get("type", ""),
                "date": meta.get("date", "")
            }]
        )
        return vector

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_vector = self.model.encode(query, normalize_embeddings=True).tolist()
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["metadatas", "distances"]
        )
        formatted = []
        if results and results['ids']:
            for i, doc_id in enumerate(results['ids'][0]):
                meta = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 0.0
                formatted.append({
                    "id": doc_id,
                    "title": meta.get("title", ""),
                    "type": meta.get("type", ""),
                    "_distance": distance
                })
        return formatted
