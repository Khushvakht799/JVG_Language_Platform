"""
add_rule.py — Добавляет правило в документ МойПроцесс
"""

from jvg import JVGStore

store = JVGStore()
doc_id = store.find_by_name("МойПроцесс")
if not doc_id:
    print("❌ Документ не найден")
    exit()

doc = store.get(doc_id)
sm = doc["vectorograph"]["state_machine"]
sm["rules"] = [
    {"condition": "state == ГОТОВ", "action": "open_url", "action_params": {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}}
]
store.update(doc_id, doc)
print("✅ Правило добавлено")
