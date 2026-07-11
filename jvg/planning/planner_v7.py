"""
jvg/planning/planner_v7.py — Поиск плана через модель мира (исправленный)
"""

import time
import pprint
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import deque
from ..storage.store import JVGStore
from ..execution.action_executor import ActionExecutor
from ..execution.interpreter import SemanticInterpreter
from ..knowledge.world_model import WorldModel

class PlannerV7:
    def __init__(self, store: Optional[JVGStore] = None):
        self.store = store or JVGStore()
        self.world = WorldModel(store)
        self.max_plan_length = 10
        self.goal_state = None

        self.actions = [
            {
                "name": "git_add",
                "action": "run_git",
                "params": {"command": "add ."},
                "preconditions": {
                    "modified": lambda s: len(s.get("modified", [])) > 0,
                    "untracked": lambda s: len(s.get("untracked", [])) > 0
                },
                "effects": {
                    "modified": lambda s: [],
                    "untracked": lambda s: [],
                    "staged": lambda s: s.get("staged", []) + s.get("modified", []) + s.get("untracked", [])
                },
                "cost": 1
            },
            {
                "name": "git_commit",
                "action": "run_git",
                "params": {"command": 'commit -m "JVG automatic commit"'},
                "preconditions": {
                    "staged": lambda s: len(s.get("staged", [])) > 0
                },
                "effects": {
                    "staged": lambda s: [],
                    "ahead": lambda s: True
                },
                "cost": 2
            },
            {
                "name": "git_push",
                "action": "run_git",
                "params": {"command": "push"},
                "preconditions": {
                    "ahead": lambda s: s.get("ahead", False)
                },
                "effects": {
                    "ahead": lambda s: False
                },
                "cost": 3
            },
            {
                "name": "git_status",
                "action": "run_git",
                "params": {"command": "status"},
                "preconditions": {},
                "effects": {},
                "cost": 0
            }
        ]

    def set_goal(self, goal_state: Dict[str, Any]):
        self.goal_state = goal_state
        print(f"🎯 Целевое состояние: {goal_state}")

    def _apply_effects(self, state: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
        new_state = state.copy()
        for key, effect_fn in action.get("effects", {}).items():
            new_state[key] = effect_fn(state)
        return new_state

    def _check_preconditions(self, state: Dict[str, Any], action: Dict[str, Any]) -> bool:
        for _, pred_fn in action.get("preconditions", {}).items():
            if not pred_fn(state):
                return False
        return True

    def _state_to_hashable(self, state: Dict[str, Any]) -> tuple:
        """Преобразует состояние в хешируемый формат."""
        items = []
        for key, value in sorted(state.items()):
            if isinstance(value, list):
                items.append((key, tuple(value)))
            else:
                items.append((key, value))
        return tuple(items)

    def _search_plan(self, initial_state: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        queue = deque()
        queue.append((initial_state, [], 0))
        visited = set()
        visited.add(self._state_to_hashable(initial_state))

        while queue:
            state, plan, cost = queue.popleft()

            if all(state.get(k) == v for k, v in self.goal_state.items()):
                return plan

            if len(plan) >= self.max_plan_length:
                continue

            for action in self.actions:
                if self._check_preconditions(state, action):
                    new_state = self._apply_effects(state, action)
                    state_key = self._state_to_hashable(new_state)
                    if state_key not in visited:
                        visited.add(state_key)
                        new_plan = plan + [action]
                        queue.append((new_state, new_plan, cost + action.get("cost", 1)))

        return None

    def run(self, doc_id: str) -> Dict[str, Any]:
        if not self.goal_state:
            return {"status": "error", "error": "Целевое состояние не установлено"}

        print(f"🧠 Запуск планировщика с поиском...")

        jvg = self.store.get(doc_id)
        if not jvg:
            return {"status": "error", "error": f"Документ {doc_id} не найден"}

        data = jvg.get("vectorograph", {})
        evolution = data.get("evolution", {})
        history = evolution.get("history", "")

        current_facts = {}
        if history:
            lines = history.strip().split("\n")
            for line in reversed(lines):
                if "Факты:" in line:
                    try:
                        fact_part = line.split("Факты:")[1].strip()
                        current_facts = eval(fact_part)
                        break
                    except:
                        pass

        initial_state = current_facts.get("git", {})
        print(f"📊 Начальное состояние:")
        pprint.pprint(initial_state)

        plan = self._search_plan(initial_state)
        if plan is None:
            return {
                "status": "blocked",
                "goal_state": self.goal_state,
                "initial_state": initial_state,
                "reason": "План не найден"
            }

        print(f"📋 План найден: {len(plan)} шагов")
        for i, action in enumerate(plan, 1):
            print(f"  {i}. {action['name']} (cost: {action.get('cost', 1)})")

        return self._execute_plan(doc_id, plan)

    def _execute_plan(self, doc_id: str, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        for i, step in enumerate(plan, 1):
            print(f"\n--- Шаг {i}/{len(plan)}: {step['name']} ---")
            print(f"🔧 Выполнение: {step['action']} {step['params']}")

            result_dict = ActionExecutor.execute(step["action"], step.get("params", {}), doc_id=doc_id)
            result = result_dict.get("execution_result")

            new_facts = SemanticInterpreter.interpret(result, repo_path=".") if result else {}
            print(f"📊 Новые факты:")
            pprint.pprint(new_facts.get("git", {}))

            if new_facts:
                jvg = self.store.get(doc_id)
                if jvg:
                    jvg["vectorograph"]["last_fact"] = new_facts
                    history_entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Факты: {new_facts}"
                    jvg["vectorograph"]["evolution"]["history"] = jvg["vectorograph"]["evolution"].get("history", "") + "\n" + history_entry
                    self.store.update(doc_id, jvg)

            print(f"   ✅ Шаг выполнен")
            time.sleep(1)

        final_jvg = self.store.get(doc_id)
        if final_jvg:
            final_data = final_jvg.get("vectorograph", {})
            final_evolution = final_data.get("evolution", {})
            final_history = final_evolution.get("history", "")
            final_facts = {}
            if final_history:
                lines = final_history.strip().split("\n")
                for line in reversed(lines):
                    if "Факты:" in line:
                        try:
                            fact_part = line.split("Факты:")[1].strip()
                            final_facts = eval(fact_part)
                            break
                        except:
                            pass

            if all(final_facts.get("git", {}).get(k) == v for k, v in self.goal_state.items()):
                return {
                    "status": "success",
                    "goal_state": self.goal_state,
                    "plan_length": len(plan),
                    "final_state": final_facts
                }

        return {
            "status": "partial",
            "goal_state": self.goal_state,
            "plan_length": len(plan),
            "message": "План выполнен, но цель не достигнута"
        }
