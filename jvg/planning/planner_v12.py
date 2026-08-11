"""
jvg/planning/planner_v12.py — Experience-Based Planner
"""

import time
import pprint
import heapq
import json
from typing import Dict, Any, List, Optional, Callable, Tuple
from ..storage.store import JVGStore
from ..execution.action_executor import ActionExecutor
from ..execution.interpreter import SemanticInterpreter
from ..execution.git_interpreter import GitInterpreter

class PlannerV12:
    def __init__(self, store: Optional[JVGStore] = None):
        self.store = store or JVGStore()
        self.max_plan_length = 10
        self.max_iterations = 15
        self.goal_state = None
        self.experience = []  # список эпизодов: [{"state": ..., "plan": ..., "result": ..., "score": ...}]
        self.similarity_threshold = 0.7

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

    def _calculate_similarity(self, state1: Dict[str, Any], state2: Dict[str, Any]) -> float:
        """Вычисляет схожесть двух состояний."""
        if not state1 or not state2:
            return 0.0

        # Сравниваем ключевые поля
        keys = ["has_modifications", "has_untracked", "has_staged", "is_ahead", "is_behind"]
        matches = 0
        for key in keys:
            if state1.get(key) == state2.get(key):
                matches += 1

        return matches / len(keys) if keys else 0.0

    def _find_similar_experience(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ищет похожий эпизод в опыте."""
        best_match = None
        best_score = 0.0

        for episode in self.experience:
            similarity = self._calculate_similarity(state, episode.get("state", {}))
            if similarity > self.similarity_threshold and similarity > best_score:
                best_score = similarity
                best_match = episode

        if best_match:
            print(f"💡 Найден похожий эпизод (схожесть: {best_score:.2f})")
            print(f"   План: {[op['name'] for op in best_match.get('plan', [])]}")
            print(f"   Результат: {best_match.get('result', 'unknown')}")
            print(f"   Оценка: {best_match.get('score', 0)}")
            return best_match

        return None

    def _save_experience(self, state: Dict[str, Any], plan: List[Dict[str, Any]], result: str, score: float):
        """Сохраняет эпизод в опыт."""
        episode = {
            "state": state,
            "plan": plan,
            "result": result,
            "score": score,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.experience.append(episode)

        # Ограничиваем размер опыта
        if len(self.experience) > 100:
            self.experience = self.experience[-100:]

        print(f"💾 Опыт сохранён: {len(plan)} шагов, оценка: {score:.2f}")

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

        print(f"🧠 Запуск Experience-Based Planner...")
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

            # Ищем похожий опыт
            similar_episode = self._find_similar_experience(current_state)
            if similar_episode:
                # Используем план из опыта
                plan = similar_episode.get("plan", [])
                print(f"📋 Используем план из опыта: {len(plan)} шагов")
                for i, op in enumerate(plan, 1):
                    print(f"  {i}. {op['name']} (cost: {op.get('cost', 1)})")
            else:
                # Строим новый план
                plan = self._search_plan(current_state)
                if plan:
                    print(f"📋 Новый план: {len(plan)} шагов")
                    for i, op in enumerate(plan, 1):
                        print(f"  {i}. {op['name']} (cost: {op.get('cost', 1)})")

            if not plan:
                print(f"❌ План не найден")
                return {"status": "blocked", "goal_state": self.goal_state, "iterations": iteration}

            # Выполняем первый шаг
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

            # Оцениваем успешность шага
            success = result.success if result else False
            print(f"   ✅ Шаг выполнен (успех: {success})")
            time.sleep(1)

            # Если это был последний шаг, сохраняем опыт
            if len(plan) == 1:
                final_state = self._get_current_state(doc_id)
                is_goal_achieved = all(self._normalize_state(final_state).get(k) == v for k, v in self.goal_state.items())
                score = 1.0 if is_goal_achieved else 0.0
                self._save_experience(current_state, plan, "success" if is_goal_achieved else "failed", score)

        return {
            "status": "timeout",
            "goal_state": self.goal_state,
            "iterations": iteration,
            "message": f"Достигнут лимит итераций ({self.max_iterations})"
        }
