"""
jvg/planning/planner_v5.py — Универсальный когнитивный движок
"""

import time
import pprint
from typing import Dict, Any, List, Optional
from ..storage.store import JVGStore
from ..execution.action_executor import ActionExecutor
from ..execution.interpreter import SemanticInterpreter
from ..knowledge.world_model import WorldModel

class PlannerV5:
    def __init__(self, store: Optional[JVGStore] = None):
        self.store = store or JVGStore()
        self.world = WorldModel(store)
        self.max_iterations = 15
        self.goal = None

    def set_goal(self, goal: Dict[str, Any]):
        self.goal = goal
        print(f"🎯 Цель установлена: {goal}")

    def is_goal_achieved(self, facts: Dict[str, Any]) -> bool:
        if not self.goal:
            return False
        
        # Цель: репозиторий синхронизирован (чистый и без изменений)
        if self.goal.get("repository_synced"):
            git = facts.get("git", {})
            return git.get("clean", False) and not git.get("ahead", False) and not git.get("behind", False)
        
        # Цель: репозиторий чист (только локально)
        if self.goal.get("repository_clean"):
            git = facts.get("git", {})
            return git.get("clean", False)
        
        # Цель: репозиторий синхронизирован с удалённым
        if self.goal.get("repository_pushed"):
            git = facts.get("git", {})
            return not git.get("ahead", False)
        
        return False

    def get_next_step(self, facts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        git = facts.get("git", {})
        
        # Высокоуровневая логика планирования
        if self.goal.get("repository_synced"):
            # Если есть изменения — добавить
            if git.get("modified") or git.get("untracked"):
                return {
                    "action": "run_git",
                    "params": {"command": "add ."},
                    "reason": "Добавляем изменения в индекс"
                }
            # Если есть подготовленные файлы — закоммитить
            if git.get("staged"):
                return {
                    "action": "run_git",
                    "params": {"command": 'commit -m "JVG automatic commit"'},
                    "reason": "Фиксируем изменения"
                }
            # Если есть локальные коммиты — запушить
            if git.get("ahead", False):
                return {
                    "action": "run_git",
                    "params": {"command": "push"},
                    "reason": "Отправляем изменения на удалённый репозиторий"
                }
            # Если есть изменения, но они не попали в категории
            if not git.get("clean", False):
                return {
                    "action": "run_git",
                    "params": {"command": "status"},
                    "reason": "Проверяем состояние репозитория"
                }
        
        # Если цель — только локально чистый репозиторий
        if self.goal.get("repository_clean"):
            if git.get("modified") or git.get("untracked"):
                return {
                    "action": "run_git",
                    "params": {"command": "add ."},
                    "reason": "Добавляем изменения"
                }
            if git.get("staged"):
                return {
                    "action": "run_git",
                    "params": {"command": 'commit -m "JVG automatic commit"'},
                    "reason": "Фиксируем изменения"
                }
            if not git.get("clean", False):
                return {
                    "action": "run_git",
                    "params": {"command": "status"},
                    "reason": "Проверяем состояние"
                }
        
        # Если цель — только синхронизация с удалённым
        if self.goal.get("repository_pushed"):
            if git.get("ahead", False):
                return {
                    "action": "run_git",
                    "params": {"command": "push"},
                    "reason": "Отправляем изменения"
                }
            if git.get("behind", False):
                return {
                    "action": "run_git",
                    "params": {"command": "pull"},
                    "reason": "Получаем изменения с удалённого репозитория"
                }
        
        return None

    def run(self, doc_id: str) -> Dict[str, Any]:
        if not self.goal:
            return {"status": "error", "error": "Цель не установлена"}

        print(f"🧠 Запуск когнитивного планирования...")
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

            print(f"📊 Текущие факты:")
            pprint.pprint(current_facts.get("git", {}))

            if self.is_goal_achieved(current_facts):
                print(f"✅ Цель достигнута!")
                return {
                    "status": "success",
                    "goal": self.goal,
                    "iterations": iteration,
                    "final_state": current_facts
                }

            step = self.get_next_step(current_facts)
            if not step:
                print(f"❌ Нет шага для достижения цели")
                return {
                    "status": "blocked",
                    "goal": self.goal,
                    "iterations": iteration,
                    "final_state": current_facts,
                    "reason": "Нет доступных шагов"
                }

            print(f"🔧 Шаг: {step['action']} ({step['reason']})")
            result_dict = ActionExecutor.execute(step["action"], step.get("params", {}), doc_id=doc_id)
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
            "goal": self.goal,
            "iterations": iteration,
            "message": f"Достигнут лимит итераций ({self.max_iterations})"
        }
