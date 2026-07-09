"""
relation_engine.py — Активные связи (Relation Engine)
Реализует триггеры и проверки для активных рёбер графа.
"""

import json
import os
import sys
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
from jvg import JVGStore, JVGRuntime

class RelationEngine:
    def __init__(self, store: Optional[JVGStore] = None, runtime: Optional[JVGRuntime] = None):
        self.store = store or JVGStore()
        self.runtime = runtime or JVGRuntime()
        self.active_edges = []
        self.load_edges()

    def load_edges(self):
        """Загружает все активные связи из всех JVG-документов."""
        self.active_edges = []
        for item in self.store.list():
            jvg = self.store.get(item["id"])
            if not jvg:
                continue
            data = jvg.get("vectorograph", {})
            relations = data.get("relations", {})
            edges = relations.get("active_edges", [])
            for edge in edges:
                edge["_source_doc_id"] = item["id"]
                self.active_edges.append(edge)

    def check_triggers(self, doc_id: str):
        """
        Проверяет все активные связи для данного документа.
        Если условие выполнено — запускает действие.
        """
        changed = False
        for edge in self.active_edges:
            if edge.get("source") != doc_id and edge.get("target") != doc_id:
                continue

            print(f"🔍 Проверка связи: {edge.get('id', 'unnamed')}")

            # Проверяем условие
            condition_met = self._evaluate_condition(edge, doc_id)
            if condition_met:
                print(f"   ✅ Условие выполнено: {edge.get('condition', '')}")
                self._execute_action(edge, doc_id)
                changed = True

        return changed

    def _evaluate_condition(self, edge: Dict[str, Any], doc_id: str) -> bool:
        """
        Проверяет условие связи.
        Поддерживает простые сравнения: target.state == "ПРОЕКТИРОВАНИЕ"
        """
        condition = edge.get("condition", "")
        if not condition:
            return True  # Если условия нет — всегда выполняем

        try:
            # Простой парсер: если условие содержит target.state
            if "target.state" in condition:
                target_id = edge.get("target")
                if target_id == doc_id:
                    target_id = edge.get("source")
                
                target_jvg = self.store.get(target_id)
                if not target_jvg:
                    return False
                
                target_state = target_jvg.get("vectorograph", {}).get("state", {}).get("current", "")
                expected_state = condition.split('"')[1] if '"' in condition else ""
                
                return target_state == expected_state

            # Если условие содержит source.state
            if "source.state" in condition:
                source_id = edge.get("source")
                if source_id == doc_id:
                    source_id = edge.get("target")
                
                source_jvg = self.store.get(source_id)
                if not source_jvg:
                    return False
                
                source_state = source_jvg.get("vectorograph", {}).get("state", {}).get("current", "")
                expected_state = condition.split('"')[1] if '"' in condition else ""
                
                return source_state == expected_state

        except Exception as e:
            print(f"   ⚠️ Ошибка проверки условия: {e}")

        return False

    def _execute_action(self, edge: Dict[str, Any], doc_id: str):
        """
        Выполняет действие, указанное в связи.
        """
        action = edge.get("action", "")
        if not action:
            return

        print(f"   🚀 Выполнение действия: {action}")

        if action == "перевести_цель_в_выполнение":
            target_id = edge.get("target")
            if target_id == doc_id:
                target_id = edge.get("source")
            result = self.runtime.step(target_id, "ВЫПОЛНЕНИЕ", f"Автоматический переход по связи {edge.get('id', '')}")
            print(f"   ✅ Результат: {result}")

        # Добавляем запись в историю связи
        if "history" not in edge:
            edge["history"] = []
        edge["history"].append({
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "action": action,
            "source_doc": doc_id
        })

        # Сохраняем обновлённый документ
        self._save_edge(edge)

    def _save_edge(self, edge: Dict[str, Any]):
        """Сохраняет обновлённую связь обратно в JVG-документ."""
        doc_id = edge.get("_source_doc_id")
        if not doc_id:
            return

        jvg = self.store.get(doc_id)
        if not jvg:
            return

        data = jvg.get("vectorograph", {})
        relations = data.get("relations", {})
        edges = relations.get("active_edges", [])

        # Находим и обновляем связь
        for i, e in enumerate(edges):
            if e.get("id") == edge.get("id"):
                edges[i] = edge
                break

        relations["active_edges"] = edges
        data["relations"] = relations
        jvg["vectorograph"] = data

        # Сохраняем как новый документ (обновлённый)
        self.store.save(jvg)


def test_relation_engine():
    print("🧪 Тест Relation Engine")
    print("=" * 50)

    store = JVGStore()
    runtime = JVGRuntime()
    engine = RelationEngine(store, runtime)

    # Создаём тестовый JVG с активной связью
    test_jvg = {
        "vectorograph": {
            "meta": {"version": "1.0", "title": "Тест активной связи", "date": "2026-07-08", "author": "Тестер", "status": "черновик"},
            "entity": {"name": "Тестовая система", "type": "система", "purpose": "тест Relation Engine"},
            "context": {"origin": "тест", "environment": "локальная", "dependencies": []},
            "structure": {"components": [], "layers": []},
            "relations": {
                "inputs": [],
                "outputs": [],
                "connected_to": [],
                "active_edges": [
                    {
                        "id": "edge_test_1",
                        "source": "Тестовая система",
                        "target": "Тестовая цель",
                        "type": "требует",
                        "trigger": "on_state_change",
                        "condition": "target.state == \"ПРОЕКТИРОВАНИЕ\"",
                        "action": "перевести_цель_в_выполнение",
                        "history": []
                    }
                ]
            },
            "logic": {"rules": [], "algorithms": [], "decision_model": []},
            "state": {"current": "ИССЛЕДОВАНИЕ", "problems": [], "risks": []},
            "actions": {"next_steps": [], "required_resources": []},
            "evolution": {"history": "", "future_versions": []}
        }
    }

    # Сохраняем тестовый документ
    doc_id = store.save(test_jvg)
    print(f"✅ Создан документ с активной связью: {doc_id}")

    # Проверяем связи
    print("\n📋 Активные связи:")
    for edge in engine.active_edges:
        print(f"   {edge.get('id')}: {edge.get('source')} → {edge.get('target')} [{edge.get('type')}]")

    # Имитируем изменение состояния
    print("\n🔄 Меняем состояние цели...")
    # Создаём документ "Тестовая цель"
    target_jvg = {
        "vectorograph": {
            "meta": {"version": "1.0", "title": "Тестовая цель", "date": "2026-07-08", "author": "Тестер", "status": "черновик"},
            "entity": {"name": "Тестовая цель", "type": "процесс", "purpose": "проверка активной связи"},
            "state": {"current": "ПРОЕКТИРОВАНИЕ", "problems": [], "risks": []},
            "context": {"origin": "тест", "environment": "локальная", "dependencies": []},
            "structure": {"components": [], "layers": []},
            "relations": {"inputs": [], "outputs": [], "connected_to": []},
            "logic": {"rules": [], "algorithms": [], "decision_model": []},
            "actions": {"next_steps": [], "required_resources": []},
            "evolution": {"history": "", "future_versions": []}
        }
    }
    target_id = store.save(target_jvg)
    print(f"   Цель сохранена с ID: {target_id}")

    # Запускаем проверку триггеров для цели
    print("\n🔍 Проверка триггеров...")
    engine.check_triggers(target_id)

    # Проверяем состояние цели
    updated_target = store.get(target_id)
    new_state = updated_target.get("vectorograph", {}).get("state", {}).get("current", "")
    print(f"\n📊 Новое состояние цели: {new_state}")


if __name__ == "__main__":
    test_relation_engine()
