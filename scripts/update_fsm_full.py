"""
scripts/update_fsm_full.py — Обновление FSM с новыми действиями
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from jvg import JVGStore

def main():
    store = JVGStore()
    doc_id = store.find_by_name('Перезапуск_Explorer')
    if not doc_id:
        results = store.find('Перезапуск')
        if results:
            doc_id = results[0].get('id')
        else:
            print("❌ Документ не найден")
            return
    
    print(f"✅ Документ найден: {doc_id}")
    
    doc = store.get(doc_id)
    
    if "vectorograph" not in doc:
        doc["vectorograph"] = {}
    if "state_machine" not in doc["vectorograph"]:
        doc["vectorograph"]["state_machine"] = {}
    
    sm = doc["vectorograph"]["state_machine"]
    sm["initial"] = "ОЖИДАНИЕ"
    sm["states"] = ["ОЖИДАНИЕ", "НЕСТАБИЛЬНО", "ВЫПОЛНЕНИЕ", "ЗАВЕРШЕНО"]
    sm["transitions"] = [
        {"from": "ОЖИДАНИЕ", "to": "НЕСТАБИЛЬНО", "event": "system_unstable"},
        {"from": "НЕСТАБИЛЬНО", "to": "ВЫПОЛНЕНИЕ", "event": "execution_success"},
        {"from": "ВЫПОЛНЕНИЕ", "to": "ЗАВЕРШЕНО", "event": "process_complete"}
    ]
    sm["rules"] = [
        {"condition": "state == НЕСТАБИЛЬНО", "action": "run_cmd", "action_params": {"command": "taskkill /f /im explorer.exe && start /B explorer.exe"}},
        {"condition": "state == ВЫПОЛНЕНИЕ", "action": "open_url", "action_params": {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}}
    ]
    
    store.update(doc_id, doc)
    print("✅ FSM обновлена")

if __name__ == "__main__":
    main()
