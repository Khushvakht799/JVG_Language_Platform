"""
jvg/fsm/fsm_engine.py — FSM с универсальным вычислителем условий
"""

from typing import Dict, Any, List, Optional

class FSMEngine:
    def __init__(self, document: Optional[Dict[str, Any]] = None, debug: bool = False):
        self.document = document
        self.debug = debug
        self._load_from_document()

    def _load_from_document(self):
        self.states = []
        self.transitions = []
        self.initial = "ИССЛЕДОВАНИЕ"
        self.rules = []

        if not self.document:
            return

        data = self.document.get("vectorograph", {})
        fsm = data.get("state_machine", {})

        if fsm:
            self.states = fsm.get("states", [])
            self.initial = fsm.get("initial", "ИССЛЕДОВАНИЕ")
            self.transitions = fsm.get("transitions", [])
            self.rules = fsm.get("rules", [])
        else:
            self.initial = "ИССЛЕДОВАНИЕ"
            self.states = ["ИССЛЕДОВАНИЕ", "ПРОЕКТИРОВАНИЕ", "ВЫПОЛНЕНИЕ", "ЗАБЛОКИРОВАНО", "ЗАВЕРШЕНО", "ОТЛОЖЕНО"]
            self.transitions = [
                {"from": "ИССЛЕДОВАНИЕ", "to": "ПРОЕКТИРОВАНИЕ"},
                {"from": "ИССЛЕДОВАНИЕ", "to": "ОТЛОЖЕНО"},
                {"from": "ПРОЕКТИРОВАНИЕ", "to": "ВЫПОЛНЕНИЕ"},
                {"from": "ПРОЕКТИРОВАНИЕ", "to": "ЗАБЛОКИРОВАНО"},
                {"from": "ПРОЕКТИРОВАНИЕ", "to": "ОТЛОЖЕНО"},
                {"from": "ВЫПОЛНЕНИЕ", "to": "ЗАВЕРШЕНО"},
                {"from": "ВЫПОЛНЕНИЕ", "to": "ЗАБЛОКИРОВАНО"},
                {"from": "ВЫПОЛНЕНИЕ", "to": "ОТЛОЖЕНО"},
                {"from": "ЗАБЛОКИРОВАНО", "to": "ВЫПОЛНЕНИЕ"},
                {"from": "ЗАБЛОКИРОВАНО", "to": "ОТЛОЖЕНО"},
                {"from": "ОТЛОЖЕНО", "to": "ИССЛЕДОВАНИЕ"},
                {"from": "ОТЛОЖЕНО", "to": "ПРОЕКТИРОВАНИЕ"},
                {"from": "ОТЛОЖЕНО", "to": "ВЫПОЛНЕНИЕ"}
            ]

    def get_initial_state(self) -> str:
        return self.initial

    def get_available_transitions(self, current: str) -> List[Dict[str, Any]]:
        return [t for t in self.transitions if t.get("from") == current]

    def get_transition_by_facts(self, current: str, facts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        transitions = self.get_available_transitions(current)
        if not transitions:
            return None

        # Сначала пытаемся найти переход с условием
        for t in transitions:
            condition = t.get("condition")
            if condition:
                result = self._evaluate_condition(condition, facts)
                if self.debug:
                    print(f"   Проверка условия: {condition} → {result}")
                if result:
                    return t

        # Если нет подходящего условия — возвращаем первый переход
        return transitions[0]

    def _evaluate_condition(self, condition: str, facts: Dict[str, Any]) -> bool:
        """
        Универсальный вычислитель условий.
        Поддерживает:
          - fact.key == value
          - fact.key != value
          - fact.key < value
          - fact.key > value
          - fact.key <= value
          - fact.key >= value
          - fact.key in [value1, value2]
          - fact.key is None / is not None
        """
        if not condition:
            return True

        try:
            # Получаем значение из фактов
            fact_key = None
            fact_value = None
            
            # Ищем ключ факта (всегда начинается с "fact.")
            for token in condition.split():
                if token.startswith("fact."):
                    fact_key = token[5:]  # убираем "fact."
                    # Достаём значение из вложенного словаря
                    fact_value = facts
                    for part in fact_key.split('.'):
                        if isinstance(fact_value, dict):
                            fact_value = fact_value.get(part)
                        else:
                            fact_value = None
                            break
                    break

            if self.debug:
                print(f"   FACT: {fact_key} = {fact_value}")

            # Разбираем оператор
            operators = ["==", "!=", ">=", "<=", ">", "<", "in", "is"]
            for op in operators:
                if op in condition:
                    left, right = condition.split(op, 1)
                    left = left.strip()
                    right = right.strip().strip('"')
                    
                    # Если в условии нет fact. — возвращаем False
                    if not left.startswith("fact."):
                        return False
                    
                    # Преобразуем правую часть
                    if right.isdigit():
                        right = int(right)
                    elif right.lower() in ["true", "false"]:
                        right = right.lower() == "true"
                    elif right.lower() == "none":
                        right = None
                    elif right.startswith("[") and right.endswith("]"):
                        # Список значений
                        right = [v.strip().strip('"') for v in right[1:-1].split(',')]
                    
                    # Сравниваем
                    if op == "==":
                        return fact_value == right
                    elif op == "!=":
                        return fact_value != right
                    elif op == ">=":
                        return fact_value >= right
                    elif op == "<=":
                        return fact_value <= right
                    elif op == ">":
                        return fact_value > right
                    elif op == "<":
                        return fact_value < right
                    elif op == "in":
                        return fact_value in right
                    elif op == "is":
                        if right is None:
                            return fact_value is None
                        return fact_value is right

        except Exception as e:
            print(f"⚠️ Ошибка проверки условия {condition}: {e}")
            return False

        return False

    def can_transition(self, current: str, target: str) -> bool:
        for t in self.transitions:
            if t.get("from") == current and t.get("to") == target:
                return True
        return False

    def get_rules(self) -> List[Dict[str, Any]]:
        return self.rules
