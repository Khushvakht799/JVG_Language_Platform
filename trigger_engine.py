"""
trigger_engine.py — Движок триггеров с режимом диагностики
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '01_toolchain', 'storage'))
sys.path.append(os.path.join(BASE_DIR, '03_runtime'))

from store import JVGStore
from runtime import JVGRuntime

class TriggerEngine:
    def __init__(self, store: Optional[JVGStore] = None, runtime: Optional[JVGRuntime] = None, debug: bool = False):
        self.store = store or JVGStore()
        self.runtime = runtime or JVGRuntime()
        self.debug = debug

    def check_triggers(self, doc_id: str) -> Dict[str, Any]:
        """Проверяет и выполняет триггеры для документа с полной диагностикой."""
        jvg = self.store.get(doc_id)
        if not jvg:
            return {"status": "error", "message": f"Документ {doc_id} не найден"}

        doc_name = jvg.get("vectorograph", {}).get("entity", {}).get("name", "")
        current_state = jvg.get("vectorograph", {}).get("state", {}).get("current", "")
        triggers = jvg.get("vectorograph", {}).get("triggers", [])

        report = {
            "doc_id": doc_id,
            "doc_name": doc_name,
            "current_state": current_state,
            "triggers_found": len(triggers),
            "triggers_checked": [],
            "triggers_fired": [],
            "new_state": current_state,
            "errors": []
        }

        if self.debug:
            print("\n=== TRIGGER DEBUG ===")
            print(f"Документ: {doc_name} ({doc_id})")
            print(f"Текущее состояние: {current_state}")
            print(f"Найдено триггеров: {len(triggers)}")
            print()

        if not triggers:
            report["errors"].append("Триггеров не найдено")
            if self.debug:
                print("⚠️ Триггеров не найдено")
            return report

        for idx, trigger in enumerate(triggers, 1):
            trigger_report = {
                "index": idx,
                "from_state": trigger.get("from", ""),
                "to_state": trigger.get("to", ""),
                "action": trigger.get("action", ""),
                "condition": trigger.get("condition", ""),
                "fired": False,
                "reason": ""
            }

            if self.debug:
                print(f"Триггер #{idx}")
                print(f"  from: {trigger_report['from_state']}")
                print(f"  to: {trigger_report['to_state']}")
                print(f"  action: {trigger_report['action']}")
                print(f"  condition: {trigger_report['condition'] or 'нет'}")

            # Проверка условия (если есть)
            condition_met = True
            if trigger.get("condition"):
                condition_met = self._evaluate_condition(trigger.get("condition"), jvg)
                if self.debug:
                    print(f"  условие: {'✅ ВЫПОЛНЕНО' if condition_met else '❌ НЕ ВЫПОЛНЕНО'}")

            # Проверка состояния
            state_match = current_state == trigger.get("from", "")
            if self.debug:
                print(f"  состояние: {'✅ СОВПАДАЕТ' if state_match else '❌ НЕ СОВПАДАЕТ'} ({current_state} == {trigger.get('from', '')})")

            if state_match and condition_met:
                trigger_report["fired"] = True
                report["triggers_fired"].append(trigger_report)
                if self.debug:
                    print("  🚀 Триггер сработал!")

                # Выполняем действие
                self._execute_action(trigger, doc_id, report)
            else:
                trigger_report["reason"] = "условие или состояние не совпали"
                report["triggers_checked"].append(trigger_report)
                if self.debug:
                    print("  ⏭️ Триггер пропущен")

            if self.debug:
                print()

        # Обновляем состояние документа, если триггер сработал
        if report["triggers_fired"]:
            updated_jvg = self.store.get(doc_id)
            report["new_state"] = updated_jvg.get("vectorograph", {}).get("state", {}).get("current", "")
            if self.debug:
                print(f"✅ Новое состояние: {report['new_state']}")

        return report

    def _evaluate_condition(self, condition: str, jvg: Dict[str, Any]) -> bool:
        """Проверяет условие триггера."""
        try:
            # Простая проверка: target.state == "ВЫПОЛНЕНИЕ"
            if "target.state" in condition:
                target_name = condition.split('"')[1] if '"' in condition else ""
                # Ищем документ по имени
                for item in self.store.list():
                    doc = self.store.get(item["id"])
                    if doc:
                        doc_name = doc.get("vectorograph", {}).get("entity", {}).get("name", "")
                        if doc_name == target_name:
                            target_state = doc.get("vectorograph", {}).get("state", {}).get("current", "")
                            expected = condition.split('"')[3] if len(condition.split('"')) > 3 else ""
                            return target_state == expected
            return True
        except Exception as e:
            if self.debug:
                print(f"   ⚠️ Ошибка проверки условия: {e}")
            return False

    def _execute_action(self, trigger: Dict[str, Any], doc_id: str, report: Dict[str, Any]):
        """Выполняет действие триггера."""
        action = trigger.get("action", "")
        to_state = trigger.get("to", "")

        if action == "перевести_цель_в_выполнение" and to_state:
            result = self.runtime.step(doc_id, to_state, f"Автоматический переход по триггеру: {action}")
            if result.get("status") != "ok":
                report["errors"].append(f"Ошибка выполнения действия: {result}")

    def explain(self, doc_id: str) -> str:
        """Генерирует текстовое объяснение, почему состояние не изменилось."""
        report = self.check_triggers(doc_id)
        if report["errors"]:
            return f"❌ Ошибка: {', '.join(report['errors'])}"

        if report["triggers_fired"]:
            return f"✅ Состояние изменено с {report['current_state']} на {report['new_state']}"

        if report["triggers_checked"]:
            reasons = [f"Триггер #{t['index']}: {t['reason']}" for t in report["triggers_checked"]]
            return f"⏭️ Состояние не изменилось. Причины:\n  " + "\n  ".join(reasons)

        return "ℹ️ Триггеров не найдено"


def test_trigger_engine():
    print("🧪 Тест Trigger Engine")
    print("=" * 50)

    store = JVGStore()
    engine = TriggerEngine(store, debug=True)

    # Находим цель
    target_id = None
    for item in store.list():
        if 'Тестовая_цель' in item['id']:
            target_id = item['id']
            break

    if not target_id:
        print("❌ Цель не найдена")
        return

    print(f"✅ Цель найдена: {target_id}")

    # Добавляем триггер в документ
    target_jvg = store.get(target_id)
    target_jvg["vectorograph"]["triggers"] = [
        {
            "event": "ready",
            "from": "ПРОЕКТИРОВАНИЕ",
            "to": "ВЫПОЛНЕНИЕ",
            "action": "перевести_цель_в_выполнение"
        }
    ]
    store.save(target_jvg)
    print("✅ Триггер добавлен в документ")

    # Проверяем триггеры
    engine.check_triggers(target_id)

if __name__ == "__main__":
    test_trigger_engine()
