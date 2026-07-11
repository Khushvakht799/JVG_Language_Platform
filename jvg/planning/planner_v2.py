"""
jvg/planning/planner_v2.py — Планировщик с оценкой вариантов
"""

from typing import Dict, Any, List, Optional
from ..storage.store import JVGStore
from ..execution.action_executor import ActionExecutor
from ..execution.interpreter import SemanticInterpreter

class PlannerV2:
    def __init__(self, store: Optional[JVGStore] = None):
        self.store = store or JVGStore()
        self.goals = []
        self.strategies = []

    def analyze(self, facts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Анализирует факты и возвращает список возможных действий с оценками.
        """
        actions = []

        # Анализ Git-фактов
        git = facts.get("git", {})
        if git:
            # 1. Если есть изменённые файлы — можно добавить
            modified_count = len(git.get("modified", []))
            untracked_count = len(git.get("untracked", []))
            if modified_count > 0 or untracked_count > 0:
                actions.append({
                    "action": "run_git",
                    "params": {"command": "add ."},
                    "priority": 1,
                    "cost": 1,
                    "risk": 1,
                    "benefit": modified_count + untracked_count,
                    "reason": f"Обнаружены изменения ({modified_count} modified, {untracked_count} untracked)",
                    "score": self._calculate_score(1, 1, modified_count + untracked_count)
                })

            # 2. Если есть подготовленные файлы — можно закоммитить
            staged_count = len(git.get("staged", []))
            if staged_count > 0:
                actions.append({
                    "action": "run_git",
                    "params": {"command": 'commit -m "JVG automatic commit"'},
                    "priority": 2,
                    "cost": 2,
                    "risk": 2,
                    "benefit": staged_count * 2,
                    "reason": f"Подготовлено {staged_count} файлов для коммита",
                    "score": self._calculate_score(2, 2, staged_count * 2)
                })

            # 3. Если ветка опережает удалённую — можно запушить
            if git.get("ahead", False):
                actions.append({
                    "action": "run_git",
                    "params": {"command": "push"},
                    "priority": 3,
                    "cost": 3,
                    "risk": 3,
                    "benefit": 10,
                    "reason": "Ветка опережает удалённую",
                    "score": self._calculate_score(3, 3, 10)
                })

            # 4. Если репозиторий чист — ничего не делаем
            if git.get("clean", False):
                actions.append({
                    "action": "idle",
                    "params": {},
                    "priority": 0,
                    "cost": 0,
                    "risk": 0,
                    "benefit": 0,
                    "reason": "Репозиторий чист",
                    "score": 0
                })

        # Анализ HTTP-фактов
        if "http" in str(facts):
            status = facts.get("http", {}).get("status_code", 0)
            if status == 503:
                actions.append({
                    "action": "send_telegram",
                    "params": {"message": "⚠️ Сервер недоступен (503)"},
                    "priority": 3,
                    "cost": 1,
                    "risk": 1,
                    "benefit": 5,
                    "reason": "Сервис временно недоступен",
                    "score": self._calculate_score(1, 1, 5)
                })
            elif status == 404:
                actions.append({
                    "action": "send_telegram",
                    "params": {"message": "❌ Ресурс не найден (404)"},
                    "priority": 3,
                    "cost": 1,
                    "risk": 1,
                    "benefit": 5,
                    "reason": "Ресурс не найден",
                    "score": self._calculate_score(1, 1, 5)
                })
            elif status >= 500:
                actions.append({
                    "action": "send_telegram",
                    "params": {"message": f"⚠️ Ошибка сервера ({status})"},
                    "priority": 3,
                    "cost": 1,
                    "risk": 1,
                    "benefit": 5,
                    "reason": "Ошибка на стороне сервера",
                    "score": self._calculate_score(1, 1, 5)
                })

        # Сортируем по скору (чем выше, тем лучше)
        return sorted(actions, key=lambda x: x.get("score", 0), reverse=True)

    def _calculate_score(self, cost: int, risk: int, benefit: int) -> float:
        """
        Вычисляет скор действия.
        Чем выше скор, тем лучше.
        """
        # Базовый скор = benefit / (cost + risk + 1)
        # Чем больше польза и меньше стоимость/риск, тем выше скор
        return benefit / (cost + risk + 1)

    def choose_action(self, facts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Выбирает лучшее действие на основе оценки.
        """
        actions = self.analyze(facts)
        if not actions:
            return None
        # Выбираем действие с наивысшим скором
        return actions[0]

    def execute_plan(self, facts: Dict[str, Any], doc_id: str) -> Dict[str, Any]:
        """
        Выполняет лучший план.
        """
        action = self.choose_action(facts)
        if not action:
            return {"status": "idle", "message": "Нет подходящих действий"}

        print(f"🧠 Planner выбрал действие: {action['action']} (скор: {action.get('score', 0):.2f})")
        print(f"   Причина: {action['reason']}")
        result_dict = ActionExecutor.execute(action["action"], action.get("params", {}), doc_id=doc_id)
        result = result_dict.get("execution_result")
        new_facts = result_dict.get("facts", {})

        return {
            "status": "ok",
            "action": action["action"],
            "result": result,
            "new_facts": new_facts,
            "reason": action["reason"],
            "score": action.get("score", 0)
        }
