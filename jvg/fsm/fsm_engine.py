"""
jvg/fsm/fsm_engine.py — Движок конечного автомата для JVG
"""

from typing import Dict, Any, List, Optional

class FSMEngine:
    def __init__(self, document: Optional[Dict[str, Any]] = None):
        self.document = document
        self._load_from_document()

    def _load_from_document(self):
        """Загружает FSM из документа."""
        self.states = []
        self.transitions = {}
        self.initial = "ИССЛЕДОВАНИЕ"
        self.rules = []

        if not self.document:
            return

        data = self.document.get("vectorograph", {})
        fsm = data.get("state_machine", {})

        if fsm:
            self.states = fsm.get("states", [])
            self.initial = fsm.get("initial", "ИССЛЕДОВАНИЕ")
            self.transitions = self._build_transition_map(fsm.get("transitions", []))
            self.rules = fsm.get("rules", [])
        else:
            # Legacy FSM (обратная совместимость)
            self.initial = "ИССЛЕДОВАНИЕ"
            self.states = ["ИССЛЕДОВАНИЕ", "ПРОЕКТИРОВАНИЕ", "ВЫПОЛНЕНИЕ", "ЗАБЛОКИРОВАНО", "ЗАВЕРШЕНО", "ОТЛОЖЕНО"]
            self.transitions = {
                "ИССЛЕДОВАНИЕ": ["ПРОЕКТИРОВАНИЕ", "ОТЛОЖЕНО"],
                "ПРОЕКТИРОВАНИЕ": ["ВЫПОЛНЕНИЕ", "ЗАБЛОКИРОВАНО", "ОТЛОЖЕНО"],
                "ВЫПОЛНЕНИЕ": ["ЗАВЕРШЕНО", "ЗАБЛОКИРОВАНО", "ОТЛОЖЕНО"],
                "ЗАБЛОКИРОВАНО": ["ВЫПОЛНЕНИЕ", "ОТЛОЖЕНО"],
                "ЗАВЕРШЕНО": [],
                "ОТЛОЖЕНО": ["ИССЛЕДОВАНИЕ", "ПРОЕКТИРОВАНИЕ", "ВЫПОЛНЕНИЕ"]
            }

    def _build_transition_map(self, transitions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Строит карту переходов из списка."""
        map = {}
        for t in transitions:
            from_state = t.get("from", "")
            to_state = t.get("to", "")
            if from_state not in map:
                map[from_state] = []
            map[from_state].append(to_state)
        return map

    def get_initial_state(self) -> str:
        return self.initial

    def can_transition(self, current: str, target: str) -> bool:
        allowed = self.transitions.get(current, [])
        return target in allowed

    def get_available_transitions(self, current: str) -> List[str]:
        return self.transitions.get(current, [])

    def transition(self, current: str, target: str) -> bool:
        if self.can_transition(current, target):
            return True
        return False

    def get_rules(self) -> List[Dict[str, Any]]:
        return self.rules
