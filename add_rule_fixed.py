"""
add_rule_fixed.py — Добавляет правило в МойПроцесс по точному ID
"""

from jvg import JVGStore

store = JVGStore()

# Используем точный ID из твоего вывода
doc_id = "МойПроцесс_20260709_212159_25c457f6"

doc = store.get(doc_id)
if not doc:
    print(f"❌ Документ {doc_id} не найден")
    exit()

print(f"✅ Документ найден: {doc_id}")

# Добавляем правило
sm = doc["vectorograph"]["state_machine"]
sm["rules"] = [
    {"condition": "state == ГОТОВ", "action": "open_url", "action_params": {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}}
]
store.update(doc_id, doc)
print("✅ Правило добавлено")
