"""
jvg/planning/planner_v6.py — Планирование через модель мира
"""

import time
import pprint
from typing import Dict, Any, List, Optional
from ..storage.store import JVGStore
from ..execution.action_executor import ActionExecutor
from ..execution.interpreter import SemanticInterpreter
from ..knowledge.world_model import WorldModel

class PlannerV6:
    def __init__(self, store: Optional[JVGStore] = None):
        self.store = store or JVGStore()
        self.world = WorldModel(store)
        self.max_iterations = 15
        self.goal_state = None

    def set_goal(self, goal_state: Dict[str, Any]):
        self.goal_state = goal_state
        print(f"🎯 Целевое состояние: {goal_state}")

    def _compute_gap(self, current: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
        """
        Вычисляет разницу между текущим и целевым состоянием мира.
        """
        gap = {}
        for key, target_value in target.items():
            current_value = current.get(key)
            if current_value != target_value:
                gap[key] = {
                    "current": current_value,
                    "target": target_value,
                    "difference": True
                }
        return gap

    def _get_available_actions(self) -> List[Dict[str, Any]]:
        """
        Возвращает список доступных действий.
        """
        return [
            {"action": "run_git", "params": {"command": "status"}, "effect": "status"},
            {"action": "run_git", "params": {"command": "add ."}, "effect": "add"},
            {"action": "run_git", "params": {"command": 'commit -m "JVG automatic commit"'}, "effect": "commit"},
            {"action": "run_git", "params": {"command": "push"}, "effect": "push"},
            {"action": "run_git", "params": {"command": "pull"}, "effect": "pull"},
        ]

    def _predict_effect(self, action: Dict[str, Any], current_facts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Предсказывает эффект действия на состояние мира.
        (Пока используем эвристики, в будущем можно заменить на симуляцию)
        """
        git = current_facts.get("git", {})
        effect = current_facts.copy()
        
        if action["effect"] == "add":
            # add убирает modified и untracked, добавляет staged
            effect["git"] = git.copy()
            effect["git"]["modified"] = []
            effect["git"]["untracked"] = []
            if git.get("modified") or git.get("untracked"):
                effect["git"]["staged"] = git.get("staged", []) + git.get("modified", []) + git.get("untracked", [])
            effect["git"]["clean"] = False
        
        elif action["effect"] == "commit":
            # commit убирает staged, добавляет ahead
            effect["git"] = git.copy()
            effect["git"]["staged"] = []
            effect["git"]["ahead"] = True
            effect["git"]["clean"] = True
        
        elif action["effect"] == "push":
            # push убирает ahead, добавляет behind если есть расхождения
            effect["git"] = git.copy()
            effect["git"]["ahead"] = False
            effect["git"]["clean"] = git.get("clean", False)
        
        elif action["effect"] == "pull":
            # pull убирает behind, добавляет modified
            effect["git"] = git.copy()
            effect["git"]["behind"] = False
        
        elif action["effect"] == "status":
            # status не меняет состояние
            pass
        
        return effect

    def _calculate_distance(self, current: Dict[str, Any], target: Dict[str, Any]) -> int:
        """
        Вычисляет расстояние между состояниями.
        """
        gap = self._compute_gap(current, target)
        return len(gap)

    def choose_action(self, current_facts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Выбирает действие, которое минимизирует расстояние до целевого состояния.
        """
        if not self.goal_state:
            return None

        target = self.goal_state
        current = current_facts.get("git", {})
        
        # Если цель уже достигнута — возвращаем None
        if self._calculate_distance(current, target) == 0:
            return None

        best_action = None
        best_distance = float('inf')
        best_effect = None

        for action in self._get_available_actions():
            predicted = self._predict_effect(action, current_facts)
            predicted_git = predicted.get("git", {})
            distance = self._calculate_distance(predicted_git, target)
            
            if distance < best_distance:
                best_distance = distance
                best_action = action
                best_effect = predicted

        if best_action:
            print(f"   📊 Расстояние до цели: {self._calculate_distance(current, target)} → {best_distance}")
            return best_action

        return None

    def run(self, doc_id: str) -> Dict[str, Any]:
        if not self.goal_state:
            return {"status": "error", "error": "Целевое состояние не установлено"}

        print(f"🧠 Запуск планирования через модель мира...")
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n--- Итерация {iteration} ---")

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

            current_git = current_facts.get("git", {})
            print(f"📊 Текущее состояние Git:")
            pprint.pprint(current_git)

            # Проверяем, достигнуто ли целевое состояние
            if self._calculate_distance(current_git, self.goal_state) == 0:
                print(f"✅ Целевое состояние достигнуто!")
                return {
                    "status": "success",
                    "goal_state": self.goal_state,
                    "iterations": iteration,
                    "final_state": current_facts
                }

            action = self.choose_action(current_facts)
            if not action:
                print(f"❌ Нет действия для достижения целевого состояния")
                return {
                    "status": "blocked",
                    "goal_state": self.goal_state,
                    "iterations": iteration,
                    "final_state": current_facts,
                    "reason": "Нет доступных действий"
                }

            print(f"🔧 Шаг: {action['action']} (эффект: {action['effect']})")
            result_dict = ActionExecutor.execute(action["action"], action.get("params", {}), doc_id=doc_id)
            result = result_dict.get("execution_result")

            new_facts = SemanticInterpreter.interpret(result, repo_path=".") if result else {}
            print(f"📊 Новые факты (после выполнения):")
            pprint.pprint(new_facts.get("git", {}))

            if new_facts:
                jvg["vectorograph"]["last_fact"] = new_facts
                history_entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Факты: {new_facts}"
                jvg["vectorograph"]["evolution"]["history"] = jvg["vectorograph"]["evolution"].get("history", "") + "\n" + history_entry
                self.store.update(doc_id, jvg)

            print(f"   ✅ Шаг выполнен")
            time.sleep(1)

        return {
            "status": "timeout",
            "goal_state": self.goal_state,
            "iterations": iteration,
            "message": f"Достигнут лимит итераций ({self.max_iterations})"
        }
