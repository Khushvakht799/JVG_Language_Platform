"""
fix_runtime_fsm.py — Обновляет Runtime для использования FSMEngine
"""

import os
import re

RUNTIME_PATH = "jvg_runtime.py"

with open(RUNTIME_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Добавляем импорт FSMEngine
if "from fsm_engine import FSMEngine" not in content:
    content = content.replace(
        "from store import JVGStore",
        "from store import JVGStore\nfrom fsm_engine import FSMEngine"
    )

# Заменяем метод step на использование FSMEngine
old_step = '''
    def step(self, doc_id: str, new_state: Optional[str] = None, 
             action_result: Optional[str] = None) -> Dict[str, Any]:
        """
        Выполняет шаг с проверкой правил.
        """
        # Получаем документ для проверки переходов
        jvg = self.store.get(doc_id)
        if jvg and "vectorograph" in jvg and "state_transitions" in jvg["vectorograph"]:
            # Используем переходы из документа
            transitions = jvg["vectorograph"]["state_transitions"]
            # Временно подменяем transitions в Runtime
            original_transitions = self.runtime.state_transitions
            self.runtime.state_transitions = transitions
            result = self.runtime.step(doc_id, new_state, action_result)
            self.runtime.state_transitions = original_transitions
        else:
            # Используем стандартные переходы
            result = self.runtime.step(doc_id, new_state, action_result)
'''

new_step = '''
    def step(self, doc_id: str, new_state: Optional[str] = None, 
             action_result: Optional[str] = None) -> Dict[str, Any]:
        """
        Выполняет шаг с проверкой правил через FSMEngine.
        """
        # Получаем документ
        jvg = self.store.get(doc_id)
        if not jvg:
            return {"status": "error", "error": f"Документ {doc_id} не найден"}
        
        # Создаём FSMEngine для этого документа
        fsm = FSMEngine(jvg)
        current_state = jvg.get("vectorograph", {}).get("state", {}).get("current", fsm.get_initial_state())
        
        # Проверяем переход
        if new_state and not fsm.can_transition(current_state, new_state):
            available = fsm.get_available_transitions(current_state)
            return {
                "status": "warning",
                "doc_id": doc_id,
                "old_state": current_state,
                "new_state": current_state,
                "error": f"Недопустимый переход: {current_state} → {new_state}",
                "available": available
            }
        
        # Выполняем переход через Runtime
        result = self.runtime.step(doc_id, new_state, action_result)
        
        # Добавляем информацию о доступных переходах
        if result.get("status") == "ok":
            result["available"] = fsm.get_available_transitions(new_state or current_state)
        
        return result
'''

if old_step in content:
    content = content.replace(old_step, new_step)
    with open(RUNTIME_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Runtime обновлён: использует FSMEngine")
else:
    print("⚠️ Метод step не найден или уже изменён")
