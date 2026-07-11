"""
jvg/planning/planner_v8.py — AI-планировщик с вычисляемыми фактами
"""

import time
import pprint
import heapq
from typing import Dict, Any, List, Optional, Set, Tuple, Callable
from ..storage.store import JVGStore
from ..execution.action_executor import ActionExecutor
from ..execution.interpreter import SemanticInterpreter
from ..execution.git_interpreter import GitInterpreter

class PlannerV8:
    def __init__(self, store: Optional[JVGStore] = None):
        self.store = store or JVGStore()
        self.max_plan_length = 10
        self.goal_state = None

        # Операторы работают только с базовыми фактами
        self.operators = [
            {
                "name": "add_changes",
                "action": "run_git",
                "params": {"command": "add ."},
                "preconditions": {
                    "has_modifications": lambda s: s.get("has_modifications", False) or s.get("has_untracked", False)
                },
                "effects": {
                    "has_modifications": False,
                    "has_untracked": False,
                    "has_staged": True
                },
                "cost": 1
            },
            {
                "name": "commit_changes",
                "action": "run_git",
                "params": {"command": 'commit -m "JVG automatic commit"'},
                "preconditions": {
                    "has_staged": lambda s: s.get("has_staged", False)
                },
                "effects": {
                    "has_staged": False,
                    "is_ahead": True
                },
                "cost": 2
            },
            {
                "name": "push_changes",
                "action": "run_git",
                "params": {"command": "push"},
                "preconditions": {
                    "is_ahead": lambda s: s.get("is_ahead", False)
                },
                "effects": {
                    "is_ahead": False
                },
                "cost": 3
            },
            {
                "name": "pull_changes",
                "action": "run_git",
                "params": {"command": "pull"},
                "preconditions": {
                    "is_behind": lambda s: s.get("is_behind", False)
                },
                "effects": {
                    "is_behind": False
                },
                "cost": 3
            },
            {
                "name": "status_check",
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

    def _normalize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Вычисляет производные факты из базовых.
        """
        normalized = state.copy()
        # is_clean вычисляется из базовых фактов
        normalized["is_clean"] = (
            not normalized.get("has_modifications", False) and
            not normalized.get("has_untracked", False) and
            not normalized.get("has_staged", False)
        )
        return normalized

    def _apply_effects(self, state: Dict[str, Any], operator: Dict[str, Any]) -> Dict[str, Any]:
        new_state = state.copy()
        for key, value in operator.get("effects", {}).items():
            if isinstance(value, Callable):
                new_state[key] = value(state)
            else:
                new_state[key] = value
        return self._normalize_state(new_state)

    def _check_preconditions(self, state: Dict[str, Any], operator: Dict[str, Any]) -> bool:
        for _, pred in operator.get("preconditions", {}).items():
            if isinstance(pred, Callable):
                if not pred(state):
                    return False
            else:
                if state.get(pred) != True:
                    return False
        return True

    def _state_to_hashable(self, state: Dict[str, Any]) -> tuple:
        items = []
        for key, value in sorted(state.items()):
            if isinstance(value, list):
                items.append((key, tuple(value)))
            else:
                items.append((key, value))
        return tuple(items)

    def _heuristic(self, state: Dict[str, Any]) -> int:
        if not self.goal_state:
            return 0
        distance = 0
        for key, target_value in self.goal_state.items():
            if state.get(key) != target_value:
                distance += 1
        return distance

    def _search_plan(self, initial_state: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        if not self.goal_state:
            return None

        normalized_initial = self._normalize_state(initial_state)

        if all(normalized_initial.get(k) == v for k, v in self.goal_state.items()):
            return []

        heap = []
        start_f = self._heuristic(normalized_initial)
        heapq.heappush(heap, (start_f, 0, normalized_initial, []))
        visited = {}
        visited[self._state_to_hashable(normalized_initial)] = 0

        while heap:
            f_cost, g_cost, state, plan = heapq.heappop(heap)

            if len(plan) >= self.max_plan_length:
                continue

            for operator in self.operators:
                if self._check_preconditions(state, operator):
                    new_state = self._apply_effects(state, operator)
                    state_key = self._state_to_hashable(new_state)
                    new_g_cost = g_cost + operator.get("cost", 1)

                    if state_key in visited and visited[state_key] <= new_g_cost:
                        continue

                    visited[state_key] = new_g_cost
                    new_plan = plan + [operator]
                    new_f = new_g_cost + self._heuristic(new_state)

                    if all(new_state.get(k) == v for k, v in self.goal_state.items()):
                        return new_plan

                    heapq.heappush(heap, (new_f, new_g_cost, new_state, new_plan))

        return None

    def run(self, doc_id: str) -> Dict[str, Any]:
        if not self.goal_state:
            return {"status": "error", "error": "Целевое состояние не установлено"}

        print(f"🧠 Запуск A* планировщика с вычисляемыми фактами...")

        # Получаем актуальное состояние из GitInterpreter
        git_facts = GitInterpreter.get_current_status()
        git_state = git_facts.get("git", {})

        print(f"📊 Актуальное состояние Git (из GitInterpreter):")
        pprint.pprint(git_state)

        # Преобразуем Git-состояние в абстрактное состояние
        initial_state = {
            "has_modifications": len(git_state.get("modified", [])) > 0,
            "has_untracked": len(git_state.get("untracked", [])) > 0,
            "has_staged": len(git_state.get("staged", [])) > 0,
            "is_ahead": git_state.get("ahead", False),
            "is_behind": git_state.get("behind", False)
        }

        print(f"📊 Начальное абстрактное состояние:")
        pprint.pprint(initial_state)

        plan = self._search_plan(initial_state)
        if plan is None:
            return {
                "status": "blocked",
                "goal_state": self.goal_state,
                "initial_state": initial_state,
                "reason": "План не найден"
            }

        print(f"📋 План найден: {len(plan)} шагов (A*)")
        for i, op in enumerate(plan, 1):
            print(f"  {i}. {op['name']} (cost: {op.get('cost', 1)})")

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

            final_git = final_facts.get("git", {})
            # Проверяем цель с вычисляемыми фактами
            is_clean = (
                len(final_git.get("modified", [])) == 0 and
                len(final_git.get("untracked", [])) == 0 and
                len(final_git.get("staged", [])) == 0
            )
            is_ahead = final_git.get("ahead", False)
            is_behind = final_git.get("behind", False)

            if is_clean and not is_ahead and not is_behind:
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
