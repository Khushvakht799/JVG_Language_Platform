"""
jvg/planning/planner.py — Планировщик действий на основе фактов (с Git-логикой)
"""

from typing import Dict, Any, List, Optional
from ..storage.store import JVGStore
from ..execution.action_executor import ActionExecutor
from ..execution.interpreter import SemanticInterpreter

class Planner:
    def __init__(self, store: Optional[JVGStore] = None):
        self.store = store or JVGStore()
        self.executors = {}

    def analyze(self, facts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Анализирует факты и возвращает список возможных действий.
        """
        actions = []

        # Анализ Git-фактов
        git = facts.get("git", {})
        if git:
            # Если есть изменённые файлы — нужно добавить
            if git.get("modified") or git.get("untracked"):
                actions.append({
                    "action": "run_git",
                    "params": {"command": "add ."},
                    "priority": 1,
                    "reason": f"Обнаружены изменения ({len(git.get('modified', []))} modified, {len(git.get('untracked', []))} untracked)"
                })
            # Если есть подготовленные файлы — нужно закоммитить
            elif git.get("staged"):
                actions.append({
                    "action": "run_git",
                    "params": {"command": 'commit -m "JVG automatic commit"'},
                    "priority": 2,
                    "reason": f"Подготовлено {len(git.get('staged', []))} файлов для коммита"
                })
            # Если ветка опережает удалённую — нужно запушить
            elif git.get("ahead"):
                actions.append({
                    "action": "run_git",
                    "params": {"command": "push"},
                    "priority": 3,
                    "reason": "Ветка опережает удалённую"
                })
            # Если репозиторий чист — ничего не делаем
            elif git.get("clean"):
                actions.append({
                    "action": "idle",
                    "params": {},
                    "priority": 0,
                    "reason": "Репозиторий чист"
                })

        # Анализ HTTP-фактов
        if "http" in str(facts):
            status = facts.get("http", {}).get("status_code", 0)
            if status == 503:
                actions.append({
                    "action": "send_telegram",
                    "params": {"message": "⚠️ Сервер недоступен (503)"},
                    "priority": 3,
                    "reason": "Сервис временно недоступен"
                })
            elif status == 404:
                actions.append({
                    "action": "send_telegram",
                    "params": {"message": "❌ Ресурс не найден (404)"},
                    "priority": 3,
                    "reason": "Ресурс не найден"
                })
            elif status >= 500:
                actions.append({
                    "action": "send_telegram",
                    "params": {"message": f"⚠️ Ошибка сервера ({status})"},
                    "priority": 3,
                    "reason": "Ошибка на стороне сервера"
                })

        return sorted(actions, key=lambda x: x["priority"], reverse=True)

    def choose_action(self, facts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Выбирает лучшее действие на основе фактов.
        """
        actions = self.analyze(facts)
        if not actions:
            return None
        # Выбираем действие с наивысшим приоритетом
        return actions[0]

    def execute_plan(self, facts: Dict[str, Any], doc_id: str) -> Dict[str, Any]:
        """
        Выполняет план действий на основе фактов.
        """
        action = self.choose_action(facts)
        if not action:
            return {"status": "idle", "message": "Нет подходящих действий"}

        print(f"🧠 Planner выбрал действие: {action['action']} ({action['reason']})")
        result_dict = ActionExecutor.execute(action["action"], action.get("params", {}), doc_id=doc_id)
        result = result_dict.get("execution_result")
        new_facts = result_dict.get("facts", {})

        return {
            "status": "ok",
            "action": action["action"],
            "result": result,
            "new_facts": new_facts,
            "reason": action["reason"]
        }
