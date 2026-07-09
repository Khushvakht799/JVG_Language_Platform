"""
jvg/cli/fsm.py — Команды для управления FSM (с update)
"""

import sys
import json
from ..storage.store import JVGStore
from ..fsm.fsm_engine import FSMEngine

def show(doc_id: str):
    store = JVGStore()
    doc = store.get(doc_id)
    if not doc:
        print(f"❌ Документ {doc_id} не найден")
        return
    fsm = doc.get("vectorograph", {}).get("state_machine", {})
    if not fsm:
        print("ℹ️ FSM не найдена")
        return
    print(json.dumps(fsm, indent=2, ensure_ascii=False))

def add_transition(doc_id: str, from_state: str, to_state: str, action: str = None, condition: str = None):
    store = JVGStore()
    doc = store.get(doc_id)
    if not doc:
        print(f"❌ Документ {doc_id} не найден")
        return
    
    if "vectorograph" not in doc:
        doc["vectorograph"] = {}
    if "state_machine" not in doc["vectorograph"]:
        doc["vectorograph"]["state_machine"] = {
            "initial": "ОЖИДАНИЕ",
            "states": [],
            "transitions": []
        }
    
    sm = doc["vectorograph"]["state_machine"]
    transition = {"from": from_state, "to": to_state}
    if condition:
        transition["condition"] = condition
    if action:
        transition["action"] = action
    
    sm["transitions"].append(transition)
    
    if from_state not in sm.get("states", []):
        sm["states"].append(from_state)
    if to_state not in sm.get("states", []):
        sm["states"].append(to_state)
    if not sm.get("initial"):
        sm["initial"] = from_state
    
    # Обновляем существующий документ
    store.update(doc_id, doc)
    print(f"✅ Переход добавлен: {from_state} → {to_state}")

def list_transitions(doc_id: str):
    store = JVGStore()
    doc = store.get(doc_id)
    if not doc:
        print(f"❌ Документ {doc_id} не найден")
        return
    fsm = FSMEngine(doc)
    current = doc.get("vectorograph", {}).get("state", {}).get("current", fsm.get_initial_state())
    available = fsm.get_available_transitions(current)
    print(f"Текущее состояние: {current}")
    print(f"Доступные переходы: {available if available else '(нет)'}")

def validate(doc_id: str):
    store = JVGStore()
    doc = store.get(doc_id)
    if not doc:
        print(f"❌ Документ {doc_id} не найден")
        return
    fsm = doc.get("vectorograph", {}).get("state_machine", {})
    if not fsm:
        print("ℹ️ FSM не найдена")
        return
    errors = []
    for t in fsm.get("transitions", []):
        if "from" not in t:
            errors.append("Переход без 'from'")
        if "to" not in t:
            errors.append("Переход без 'to'")
        if t.get("from") not in fsm.get("states", []):
            errors.append(f"Состояние '{t.get('from')}' не найдено в states")
        if t.get("to") not in fsm.get("states", []):
            errors.append(f"Состояние '{t.get('to')}' не найдено в states")
    if errors:
        print("❌ Ошибки в FSM:")
        for e in errors:
            print(f"  {e}")
    else:
        print("✅ FSM корректна")

def main():
    if len(sys.argv) < 2:
        print("""
FSM CLI

Использование:
    python -m jvg.cli.fsm show <doc_id>
    python -m jvg.cli.fsm list <doc_id>
    python -m jvg.cli.fsm add <doc_id> <from> <to> [action] [condition]
    python -m jvg.cli.fsm validate <doc_id>
""")
        return
    cmd = sys.argv[1]
    if cmd == "show" and len(sys.argv) > 2:
        show(sys.argv[2])
    elif cmd == "list" and len(sys.argv) > 2:
        list_transitions(sys.argv[2])
    elif cmd == "add" and len(sys.argv) >= 5:
        doc_id = sys.argv[2]
        from_state = sys.argv[3]
        to_state = sys.argv[4]
        action = sys.argv[5] if len(sys.argv) > 5 else None
        condition = sys.argv[6] if len(sys.argv) > 6 else None
        add_transition(doc_id, from_state, to_state, action, condition)
    elif cmd == "validate" and len(sys.argv) > 2:
        validate(sys.argv[2])
    else:
        print(f"❌ Неизвестная команда или недостаточно аргументов: {cmd}")

if __name__ == "__main__":
    main()
