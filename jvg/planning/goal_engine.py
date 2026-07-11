"""
jvg/planning/goal_engine.py — Движок целей и планирования
"""

from typing import Dict, Any, List, Optional
from ..storage.store import JVGStore
from ..fsm.fsm_engine import FSMEngine
from ..events.event_bus import EventBus

class GoalEngine:
    def __init__(self, store: Optional[JVGStore] = None):
        self.store = store or JVGStore()
        self.goals = {}

    def register_goal(self, goal_id: str, condition: str, action: str, target_state: str):
        """
        Регистрирует цель.
        """
        self.goals[goal_id] = {
            "condition": condition,
            "action": action,
            "target_state": target_state,
            "active": True
        }
        print(f"🎯 Цель зарегистрирована: {goal_id}")

    def evaluate(self, facts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Проверяет все цели на основе фактов.
        Возвращает список целей, которые нужно выполнить.
        """
        triggered = []
        for goal_id, goal in self.goals.items():
            if not goal["active"]:
                continue
            if self._evaluate_condition(goal["condition"], facts):
                triggered.append({
                    "goal_id": goal_id,
                    "action": goal["action"],
                    "target_state": goal["target_state"]
                })
        return triggered

    def _evaluate_condition(self, condition: str, facts: Dict[str, Any]) -> bool:
        """
        Проверяет условие на основе фактов.
        """
        try:
            if " == " in condition:
                left, right = condition.split(" == ", 1)
                left = left.strip()
                right = right.strip().strip('"')
                if left.startswith("fact."):
                    fact_key = left[5:]
                    fact_value = facts
                    for part in fact_key.split('.'):
                        if isinstance(fact_value, dict):
                            fact_value = fact_value.get(part)
                        else:
                            fact_value = None
                            break
                    if right.isdigit():
                        right = int(right)
                    elif right.lower() in ["true", "false"]:
                        right = right.lower() == "true"
                    return fact_value == right
            elif " != " in condition:
                left, right = condition.split(" != ", 1)
                left = left.strip()
                right = right.strip().strip('"')
                if left.startswith("fact."):
                    fact_key = left[5:]
                    fact_value = facts
                    for part in fact_key.split('.'):
                        if isinstance(fact_value, dict):
                            fact_value = fact_value.get(part)
                        else:
                            fact_value = None
                            break
                    if right.isdigit():
                        right = int(right)
                    elif right.lower() in ["true", "false"]:
                        right = right.lower() == "true"
                    return fact_value != right
        except Exception:
            return False
        return False

    def execute_goals(self, goals: List[Dict[str, Any]], doc_id: str) -> List[Dict[str, Any]]:
        """
        Выполняет цели.
        """
        results = []
        for goal in goals:
            print(f"🎯 Выполнение цели: {goal['goal_id']}")
            EventBus.publish(f"goal.{goal['goal_id']}", {
                "doc_id": doc_id,
                "action": goal["action"],
                "target_state": goal["target_state"]
            })
            results.append({
                "goal_id": goal["goal_id"],
                "executed": True
            })
        return results
