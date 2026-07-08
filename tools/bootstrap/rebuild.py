"""
rebuild.py — Пересборка индексов JVG
"""

import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

def main():
    print("🔨 Пересборка индексов...")
    
    try:
        from jvg import JVGStore, JVGVectorizer, JVGRankingEngine
        
        store = JVGStore()
        vectorizer = JVGVectorizer()
        ranking = JVGRankingEngine()
        
        items = store.list()
        print(f"📁 Найдено документов: {len(items)}")
        
        for item in items:
            doc_id = item["id"]
            jvg = store.get(doc_id)
            if jvg:
                vectorizer.vectorize(jvg, doc_id)
                ranking.index_jvg(jvg, doc_id)
                print(f"  ✅ {doc_id}")
        
        print("✅ Пересборка завершена")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
