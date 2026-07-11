"""
jvg/planning/goal_planner.py — Планировщик целей
"""

from typing import Dict, Any, List, Optional
from ..storage.store import JVGStore
from ..execution.action_card import ActionCard

class GoalPlanner:
    def __init__(self, store: Optional[JVGStore] = None):
        self.store = store or JVGStore()
        self.available_agents = []
        self._load_agents()

    def _load_agents(self):
        """Загружает доступных агентов из хранилища."""
        for item in self.store.list():
            if "агент" in item.get("type", "").lower() or "процесс" in item.get("type", "").lower():
                self.available_agents.append(item.get("id"))

    def plan(self, goal: str, facts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Строит план достижения цели на основе фактов.
        """
        print(f"\n🎯 Планирование цели: {goal}")
        print(f"📊 Текущие факты: {facts}")

        plan = []

        # Простейший планировщик:
        # 1. Проверяем, есть ли цель в фактах
        if "http.status_code" in str(facts):
            status = facts.get("http", {}).get("status_code", 0)
            if status != 200:
                plan.append({
                    "step": 1,
                    "action": "run_repair",
                    "agent": "Ремонт",
                    "reason": f"HTTP статус {status}, требуется восстановление"
                })
                plan.append({
                    "step": 2,
                    "action": "check_repair",
                    "agent": "Монитор",
                    "reason": "Проверка после ремонта"
                })
            else:
                plan.append({
                    "step": 1,
                    "action": "idle",
                    "agent": "Монитор",
                    "reason": "Сервис работает, цель достигнута"
                })
        else:
            plan.append({
                "step": 1,
                "action": "diagnose",
                "agent": "Монитор",
                "reason": "Недостаточно фактов, требуется диагностика"
            })

        return plan

    def evaluate_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Оценивает план по риску, стоимости и времени.
        """
        total_risk = 0
        total_steps = len(plan)
        can_execute = True

        for step in plan:
            action = step.get("action", "")
            if action == "run_repair":
                total_risk += 3
            elif action == "check_repair":
                total_risk += 1
            elif action == "diagnose":
                total_risk += 2

        return {
            "total_steps": total_steps,
            "total_risk": total_risk,
            "can_execute": can_execute,
            "recommendation": "Выполнить" if total_risk < 8 else "Требуется подтверждение"
        }
