"""
test_preference.py — Проверка Preference Profile в ранжировании
"""

import sys
import os

# Добавляем пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, '02_search', 'ranking'))
sys.path.insert(0, os.path.join(BASE_DIR, '02_search', 'vectorizer'))
sys.path.insert(0, os.path.join(BASE_DIR, '01_toolchain', 'storage'))

from preference import PreferenceProfile, ARCHITECT_PROFILE
from ranking import JVGRankingEngine

ranking = JVGRankingEngine()
print("✅ Ranking Engine загружен")

# Поиск с профилем архитектора
results = ranking.search("система", profile=ARCHITECT_PROFILE, top_k=3)
print(f"✅ Поиск с профилем: {len(results)} результатов")
for r in results[:2]:
    title = r.get("title", "<без названия>")
    score = r["score"]
    print(f"  {title} — скор: {score:.4f}")
