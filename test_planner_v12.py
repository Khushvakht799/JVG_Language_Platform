"""
test_planner_v12.py — Систематическое тестирование Planner V12
"""

import time
import pprint
import subprocess
from typing import Dict, Any, List
from jvg import PlannerV12, JVGStore

class PlannerTest:
    def __init__(self):
        self.store = JVGStore()
        self.planner = PlannerV12(self.store)
        self.doc_id = "GitAgent_20260711_114248_5bed76d1"
        self.results = []

    def setup_state(self, state: Dict[str, Any]):
        """
        Устанавливает состояние Git для теста.
        """
        commands = []
        if state.get("has_modifications"):
            commands.append("echo '# modification' >> test_mod.txt")
        if state.get("has_untracked"):
            commands.append("echo '# untracked' > test_untracked.txt")
        if state.get("has_staged"):
            commands.append("git add test_mod.txt")
        if state.get("is_ahead"):
            commands.append("git commit -m 'test commit'")
        if state.get("is_behind"):
            # Имитируем behind, создавая коммит в удалённом репозитории
            # (упрощённо: просто создаём локальный коммит, который не пушили)
            pass

        for cmd in commands:
            subprocess.run(cmd, shell=True, capture_output=True)

    def reset_state(self):
        """
        Сбрасывает состояние Git (удаляет тестовые файлы, откатывает коммиты).
        """
        # Удаляем тестовые файлы
        subprocess.run("rm -f test_*.txt", shell=True, capture_output=True)
        # Сбрасываем индекс
        subprocess.run("git reset --hard HEAD", shell=True, capture_output=True)
        # Удаляем последний коммит если он тестовый
        # (упрощённо)

    def run_test(self, name: str, state: Dict[str, Any], expected_plan: List[str]):
        """
        Запускает один тест.
        """
        print(f"\n{'='*60}")
        print(f"🧪 Тест: {name}")
        print(f"   Состояние: {state}")
        print(f"   Ожидаемый план: {expected_plan}")
        print(f"{'='*60}")

        # Устанавливаем состояние
        self.setup_state(state)

        # Запускаем Planner
        self.planner.set_goal({
            "is_clean": True,
            "is_ahead": False,
            "is_behind": False
        })
        self.planner.max_iterations = 10

        # Выполняем планирование
        result = self.planner.run(self.doc_id)

        # Проверяем результат
        if result.get("status") == "success":
            print(f"✅ Тест пройден (цель достигнута)")
            passed = True
        else:
            print(f"❌ Тест пройден (цель не достигнута)")
            passed = False

        # Сохраняем результат
        self.results.append({
            "name": name,
            "state": state,
            "expected_plan": expected_plan,
            "status": result.get("status"),
            "iterations": result.get("iterations", 0),
            "passed": passed,
            "experience": self.planner.experience.copy()
        })

        # Сбрасываем состояние
        self.reset_state()
        time.sleep(1)

        return passed

    def run_all_tests(self):
        """
        Запускает все тесты.
        """
        tests = [
            {
                "name": "Чистый репозиторий",
                "state": {
                    "has_modifications": False,
                    "has_untracked": False,
                    "has_staged": False,
                    "is_ahead": False,
                    "is_behind": False
                },
                "expected_plan": []
            },
            {
                "name": "Неотслеживаемые файлы",
                "state": {
                    "has_modifications": False,
                    "has_untracked": True,
                    "has_staged": False,
                    "is_ahead": False,
                    "is_behind": False
                },
                "expected_plan": ["add_changes", "commit_changes", "push_changes"]
            },
            {
                "name": "Подготовленные файлы",
                "state": {
                    "has_modifications": False,
                    "has_untracked": False,
                    "has_staged": True,
                    "is_ahead": False,
                    "is_behind": False
                },
                "expected_plan": ["commit_changes", "push_changes"]
            },
            {
                "name": "Локальный коммит (ahead)",
                "state": {
                    "has_modifications": False,
                    "has_untracked": False,
                    "has_staged": False,
                    "is_ahead": True,
                    "is_behind": False
                },
                "expected_plan": ["push_changes"]
            },
            {
                "name": "Изменённые файлы",
                "state": {
                    "has_modifications": True,
                    "has_untracked": False,
                    "has_staged": False,
                    "is_ahead": False,
                    "is_behind": False
                },
                "expected_plan": ["add_changes", "commit_changes", "push_changes"]
            },
            {
                "name": "Смешанное состояние",
                "state": {
                    "has_modifications": True,
                    "has_untracked": True,
                    "has_staged": False,
                    "is_ahead": False,
                    "is_behind": False
                },
                "expected_plan": ["add_changes", "commit_changes", "push_changes"]
            }
        ]

        print("\n" + "="*60)
        print("🚀 Запуск серии тестов Planner V12")
        print("="*60)

        for test in tests:
            self.run_test(test["name"], test["state"], test["expected_plan"])

        # Выводим итоги
        print("\n" + "="*60)
        print("📊 Итоги тестирования")
        print("="*60)
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        print(f"  Пройдено: {passed}/{total} ({passed/total*100:.1f}%)")

        for result in self.results:
            status = "✅" if result["passed"] else "❌"
            print(f"  {status} {result['name']} (итераций: {result['iterations']})")

        # Показываем накопленный опыт
        print(f"\n📚 Накопленный опыт: {len(self.planner.experience)} эпизодов")
        for i, episode in enumerate(self.planner.experience, 1):
            print(f"  {i}. {[op['name'] for op in episode.get('plan', [])]} → {episode.get('result', 'unknown')}")

        return self.results

def main():
    tester = PlannerTest()
    results = tester.run_all_tests()

if __name__ == "__main__":
    main()
