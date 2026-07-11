"""
jvg/planning/planner_v3.py — Планировщик на основе целей
"""

from typing import Dict, Any, List, Optional
from ..storage.store import JVGStore
from ..execution.action_executor import ActionExecutor

class PlannerV3:
    def __init__(self, store: Optional[JVGStore] = None):
        self.store = store or JVGStore()
        self.goals = []
        self.plans = []

    def set_goal(self, goal: Dict[str, Any]):
        """
        Устанавливает цель для планировщика.
        """
        self.goals.append(goal)
        print(f"🎯 Цель установлена: {goal}")

    def analyze(self, facts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Анализирует факты и строит план достижения цели.
        """
        plans = []
        git = facts.get("git", {})

        # Если цель — чистый репозиторий
        if self.goals and "clean_repo" in str(self.goals):
            if git.get("clean", False):
                plans.append({
                    "action": "idle",
                    "params": {},
                    "cost": 0,
                    "confidence": 1.0,
                    "reason": "Репозиторий уже чист"
                })
            else:
                # Шаг 1: Добавить изменения
                if git.get("modified") or git.get("untracked"):
                    plans.append({
                        "action": "run_git",
                        "params": {"command": "add ."},
                        "cost": 1,
                        "confidence": 0.9,
                        "reason": "Добавляем изменения"
                    })
                # Шаг 2: Закоммитить
                if git.get("staged"):
                    plans.append({
                        "action": "run_git",
                        "params": {"command": 'commit -m "JVG automatic commit"'},
                        "cost": 2,
                        "confidence": 0.8,
                        "reason": "Фиксируем изменения"
                    })
                # Шаг 3: Запушить
                if git.get("ahead", False):
                    plans.append({
                        "action": "run_git",
                        "params": {"command": "push"},
                        "cost": 3,
                        "confidence": 0.7,
                        "reason": "Отправляем изменения"
                    })
                # Шаг 4: Проверить статус
                plans.append({
                    "action": "run_git",
                    "params": {"command": "status"},
                    "cost": 0,
                    "confidence": 1.0,
                    "reason": "Проверяем состояние"
                })

        # Если цель — отправить уведомление
        if self.goals and "notify" in str(self.goals):
            if "http" in str(facts):
                status = facts.get("http", {}).get("status_code", 0)
                if status >= 500:
                    plans.append({
                        "action": "send_telegram",
                        "params": {"message": f"⚠️ Ошибка сервера ({status})"},
                        "cost": 1,
                        "confidence": 1.0,
                        "reason": "Уведомляем о проблеме"
                    })

        return plans

    def choose_plan(self, facts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Выбирает лучший план достижения цели.
        """
        plans = self.analyze(facts)
        if not plans:
            return None
        # Выбираем план с наименьшей стоимостью и высокой уверенностью
        best_plan = min(plans, key=lambda x: (x.get("cost", 0), -x.get("confidence", 0)))
        return best_plan

    def execute_plan(self, facts: Dict[str, Any], doc_id: str) -> Dict[str, Any]:
        """
        Выполняет план.
        """
        plan = self.choose_plan(facts)
        if not plan:
            return {"status": "idle", "message": "Нет плана для достижения цели"}

        print(f"🧠 План: {plan['action']} ({plan['reason']})")
        result_dict = ActionExecutor.execute(plan["action"], plan.get("params", {}), doc_id=doc_id)
        result = result_dict.get("execution_result")

        return {
            "status": "ok",
            "action": plan["action"],
            "result": result,
            "reason": plan["reason"],
            "cost": plan.get("cost", 0)
        }
