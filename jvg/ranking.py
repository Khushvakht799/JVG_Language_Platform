"""
ranking.py — Ранжирование JVG (исправленный импорт)
"""

import os
import sys
from typing import Dict, Any, List, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

from .config import CHROMA_DB_PATH, MODEL_NAME

class JVGRankingEngine:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(CHROMA_DB_PATH)
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))
        self.model = SentenceTransformer(MODEL_NAME)
        self.layers = {
            "semantic": {"collection": "jvg_vectors", "weight": 0.30},
            "logic": {"collection": "jvg_logic", "weight": 0.25},
            "structure": {"collection": "jvg_structure", "weight": 0.15},
            "actions": {"collection": "jvg_actions", "weight": 0.15},
            "context": {"collection": "jvg_context", "weight": 0.10},
            "evolution": {"collection": "jvg_evolution", "weight": 0.03},
            "state": {"collection": "jvg_state", "weight": 0.02}
        }
        self._ensure_collections()

    def _ensure_collections(self):
        for layer_name, layer_info in self.layers.items():
            try:
                self.client.get_collection(layer_info["collection"])
            except Exception:
                self.client.create_collection(
                    name=layer_info["collection"],
                    metadata={"hnsw:space": "cosine"}
                )

    def index_jvg(self, jvg: Dict[str, Any], doc_id: str):
        data = jvg.get("vectorograph", {})
        for layer_name, layer_info in self.layers.items():
            collection = self.client.get_collection(layer_info["collection"])
            text = self._get_layer_text(data, layer_name)
            if text:
                vector = self.model.encode(text, normalize_embeddings=True).tolist()
                collection.add(
                    ids=[f"{doc_id}_{layer_name}"],
                    embeddings=[vector],
                    metadatas=[{
                        "doc_id": doc_id,
                        "layer": layer_name,
                        "title": data.get("meta", {}).get("title", ""),
                        "type": data.get("entity", {}).get("type", "")
                    }]
                )

    def _get_layer_text(self, data: Dict[str, Any], layer: str) -> str:
        if layer == "semantic":
            entity = data.get("entity", {})
            context = data.get("context", {})
            return " ".join([entity.get("name", ""), entity.get("purpose", ""), context.get("origin", "")])
        elif layer == "logic":
            logic = data.get("logic", {})
            return " ".join([" ".join(logic.get("rules", [])), " ".join(logic.get("algorithms", [])), " ".join(logic.get("decision_model", []))])
        elif layer == "structure":
            structure = data.get("structure", {})
            return " ".join([" ".join(structure.get("components", [])), " ".join(structure.get("layers", []))])
        elif layer == "actions":
            actions = data.get("actions", {})
            return " ".join([" ".join(actions.get("next_steps", [])), " ".join(actions.get("required_resources", []))])
        elif layer == "context":
            context = data.get("context", {})
            return " ".join([context.get("environment", ""), " ".join(context.get("dependencies", []))])
        elif layer == "evolution":
            evolution = data.get("evolution", {})
            return " ".join([evolution.get("history", ""), " ".join(evolution.get("future_versions", []))])
        elif layer == "state":
            state = data.get("state", {})
            return " ".join([state.get("current", ""), " ".join(state.get("problems", [])), " ".join(state.get("risks", []))])
        return ""

    def search(self, query: str, filters: Dict[str, Any] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        results_by_doc = {}
        for layer_name, layer_info in self.layers.items():
            collection = self.client.get_collection(layer_info["collection"])
            query_vector = self.model.encode(query, normalize_embeddings=True).tolist()
            try:
                raw_results = collection.query(
                    query_embeddings=[query_vector],
                    n_results=top_k * 2,
                    include=["metadatas", "distances"]
                )
                if raw_results and raw_results['ids']:
                    for i, doc_id in enumerate(raw_results['ids'][0]):
                        real_doc_id = doc_id.split('_')[0] if '_' in doc_id else doc_id
                        distance = raw_results['distances'][0][i] if raw_results['distances'] else 1.0
                        similarity = 1.0 - distance
                        if real_doc_id not in results_by_doc:
                            results_by_doc[real_doc_id] = {"layers": {}, "total": 0.0, "meta": {}}
                        results_by_doc[real_doc_id]["layers"][layer_name] = similarity
                        results_by_doc[real_doc_id]["total"] += similarity * layer_info["weight"]
                        if not results_by_doc[real_doc_id]["meta"]:
                            meta = raw_results['metadatas'][0][i] if raw_results['metadatas'] else {}
                            results_by_doc[real_doc_id]["meta"] = meta
            except Exception:
                pass

        filtered_results = []
        for doc_id, data in results_by_doc.items():
            meta = data["meta"]
            if filters:
                skip = False
                if "type" in filters and meta.get("type") != filters["type"]:
                    skip = True
                if skip:
                    continue
            filtered_results.append({
                "id": doc_id,
                "title": meta.get("title", ""),
                "type": meta.get("type", ""),
                "score": data["total"],
                "layers": data["layers"]
            })
        filtered_results.sort(key=lambda x: x["score"], reverse=True)
        return filtered_results[:top_k]
