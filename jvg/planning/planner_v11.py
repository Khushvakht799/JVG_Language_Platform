"""
jvg/planning/planner_v11.py — Reasoner + Learning
"""

import time
import pprint
import heapq
from typing import Dict, Any, List, Optional, Callable, Tuple
from ..storage.store import JVGStore
from ..execution.action_executor import ActionExecutor
from ..execution.interpreter import SemanticInterpreter
from ..execution.git_interpreter import GitInterpreter

class PlannerV11:
    def __init__(self, store: Optional[JVGStore] = None):
        self.store = store or JVGStore()
        self.max_plan_length = 10
        self.max_iterations = 15
        self.goal_state = None
        self.experience = {}  # память опыта: goal -> (plan, success_count, fail_count)
        self.decision_history = []  # история решений

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
                "cost": 1,
                "risk": 0.1,
                "description": "Добавляет все изменения в индекс"
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
                "cost": 2,
                "risk": 0.2,
                "description": "Фиксирует подготовленные изменения"
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
                "cost": 3,
                "risk": 0.3,
                "description": "Отправляет изменения на удалённый репозиторий"
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
                "cost": 3,
                "risk": 0.2,
                "description": "Получает изменения с удалённого репозитория"
            },
            {
                "name": "status_check",
                "action": "run_git",
                "params": {"command": "status"},
                "preconditions": {},
                "effects": {},
                "cost": 0,
                "risk": 0.0,
                "description": "Проверяет состояние репозитория"
            }
        ]

    def set_goal(self, goal_state: Dict[str, Any]):
        self.goal_state = goal_state
        print(f"🎯 Целевое состояние: {goal_state}")

    def _normalize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        normalized = state.copy()
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

    def _explain_plan(self, plan: List[Dict[str, Any]]) -> str:
        """Генерирует объяснение плана."""
        if not plan:
            return "Цель уже достигнута, план не требуется."

        explanation = "План состоит из следующих шагов:\n"
        for i, op in enumerate(plan, 1):
            desc = op.get("description", op["name"])
            cost = op.get("cost", 1)
            risk = op.get("risk", 0)
            explanation += f"  {i}. {desc} (стоимость: {cost}, риск: {risk:.1f})\n"

        total_cost = sum(op.get("cost", 1) for op in plan)
        total_risk = sum(op.get("risk", 0) for op in plan)
        explanation += f"\nОбщая стоимость: {total_cost}, общий риск: {total_risk:.1f}"
        explanation += f"\nКоличество шагов: {len(plan)}"

        return explanation

    def _evaluate_alternatives(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Оценивает альтернативные планы и возвращает их с объяснениями."""
        alternatives = []
        
        # Генерируем несколько возможных планов
        for operator in self.operators:
            if self._check_preconditions(state, operator):
                new_state = self._apply_effects(state, operator)
                plan = self._search_plan(new_state)
                if plan:
                    total_cost = sum(op.get("cost", 1) for op in plan) + operator.get("cost", 1)
                    total_risk = sum(op.get("risk", 0) for op in plan) + operator.get("risk", 0)
                    alternatives.append({
                        "first_step": operator["name"],
                        "plan": [operator] + plan,
                        "total_cost": total_cost,
                        "total_risk": total_risk,
                        "description": operator.get("description", operator["name"])
                    })

        # Сортируем по стоимости
        alternatives.sort(key=lambda x: (x["total_cost"], x["total_risk"]))
        return alternatives

    def _get_current_state(self, doc_id: str) -> Dict[str, Any]:
        """Получает текущее состояние из документа."""
        jvg = self.store.get(doc_id)
        if not jvg:
            return {}

        data = jvg.get("vectorograph", {})
        evolution = data.get("evolution", {})
        history = evolution.get("history", "")

        if not history:
            return {}

        lines = history.strip().split("\n")
        for line in reversed(lines):
            if "Факты:" in line:
                try:
                    fact_part = line.split("Факты:")[1].strip()
                    facts = eval(fact_part)
                    git_state = facts.get("git", {})
                    return {
                        "has_modifications": len(git_state.get("modified", [])) > 0,
                        "has_untracked": len(git_state.get("untracked", [])) > 0,
                        "has_staged": len(git_state.get("staged", [])) > 0,
                        "is_ahead": git_state.get("ahead", False),
                        "is_behind": git_state.get("behind", False)
                    }
                except:
                    pass

        return {}

    def run(self, doc_id: str) -> Dict[str, Any]:
        if not self.goal_state:
            return {"status": "error", "error": "Целевое состояние не установлено"}

        print(f"🧠 Запуск когнитивного ядра JVG (Reasoner + Learning)...")
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n--- Итерация {iteration} ---")

            current_state = self._get_current_state(doc_id)
            print(f"📊 Текущее состояние:")
            pprint.pprint(current_state)

            if not current_state:
                print(f"⚠️ Состояние не получено, выполняем наблюдение...")
                ActionExecutor.execute("run_git", {"command": "status"}, doc_id=doc_id)
                current_state = self._get_current_state(doc_id)

            normalized = self._normalize_state(current_state)
            if all(normalized.get(k) == v for k, v in self.goal_state.items()):
                print(f"✅ Цель достигнута!")
                return {"status": "success", "goal_state": self.goal_state, "iterations": iteration}

            # Проверяем опыт
            goal_key = str(sorted(self.goal_state.items()))
            if goal_key in self.experience:
                plan, success_count, fail_count = self.experience[goal_key]
                print(f"💡 Используем опыт для цели (успехов: {success_count}, неудач: {fail_count})")
                if success_count > fail_count:
                    plan_to_use = plan
                else:
                    print(f"   ⚠️ Опыт показывает низкую успешность, перепланируем...")
                    plan_to_use = None
            else:
                plan_to_use = None

            if not plan_to_use:
                # Оцениваем альтернативы
                alternatives = self._evaluate_alternatives(current_state)
                if alternatives:
                    print(f"📋 Найдено {len(alternatives)} альтернативных планов:")
                    for i, alt in enumerate(alternatives[:3], 1):
                        print(f"  {i}. {alt['description']} (стоимость: {alt['total_cost']}, риск: {alt['total_risk']:.1f})")
                    
                    # Выбираем лучший план
                    best_alternative = alternatives[0]
                    plan = best_alternative["plan"]
                    print(f"\n✅ Выбран план: {best_alternative['description']}")
                    print(f"   Общая стоимость: {best_alternative['total_cost']}, риск: {best_alternative['total_risk']:.1f}")
                else:
                    plan = self._search_plan(current_state)

                if plan:
                    # Сохраняем опыт
                    goal_key = str(sorted(self.goal_state.items()))
                    if goal_key not in self.experience:
                        self.experience[goal_key] = (plan, 0, 0)
                    print(f"💾 Опыт сохранён: {len(plan)} шагов")

            # Объясняем план
            if plan:
                print(f"\n📖 Объяснение плана:")
                print(self._explain_plan(plan))

                first_step = plan[0]
                print(f"\n🔧 Выполнение шага: {first_step['name']}")
                result_dict = ActionExecutor.execute(first_step["action"], first_step.get("params", {}), doc_id=doc_id)
                result = result_dict.get("execution_result")

                new_facts = SemanticInterpreter.interpret(result, repo_path=".") if result else {}
                print(f"📊 Результат шага:")
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
            else:
                print(f"❌ План не найден")
                return {"status": "blocked", "goal_state": self.goal_state, "iterations": iteration}

        return {
            "status": "timeout",
            "goal_state": self.goal_state,
            "iterations": iteration,
            "message": f"Достигнут лимит итераций ({self.max_iterations})"
        }
