"""
cognitive_os_core.py — Ядро Cognitive OS
"""

import os
import sys
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '..', '01_toolchain', 'document'))
sys.path.append(os.path.join(BASE_DIR, '..', '01_toolchain', 'storage'))
sys.path.append(os.path.join(BASE_DIR, '..', '02_search', 'vectorizer'))
sys.path.append(os.path.join(BASE_DIR, '..', '02_search', 'ranking'))

from compiler import JVGCompiler
from l1_adapter import L1Adapter
from l2_memory import L2Memory
from l3_models import L3Models
from l4_execution import L4Execution
from l5_audit import L5Audit

class CognitiveOS:
    def __init__(self, storage_dir: str = "jvg_store", vector_db_path: str = "jvg_chroma_db"):
        self.compiler = JVGCompiler()
        self.l1 = L1Adapter()
        self.l2 = L2Memory(storage_dir=storage_dir, vector_db_path=vector_db_path)
        self.l3 = L3Models(self.l2)
        self.l4 = L4Execution(storage_dir=storage_dir)
        self.l5 = L5Audit()

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        jvg = self.l1.event_to_jvg(event)
        audit = self.l5.validate(jvg)
        doc_id = self.l2.save(jvg)
        analysis = self.l3.analyze_state(doc_id)
        return {"doc_id": doc_id, "jvg": jvg, "audit": audit, "analysis": analysis}

    def process_text(self, text: str) -> Dict[str, Any]:
        compile_result = self.compiler.compile(text)
        if compile_result["status"] != "success":
            return {"status": "error", "errors": compile_result.get("errors", [])}
        jvg = compile_result["jvg"]
        audit = self.l5.validate(jvg)
        doc_id = self.l2.save(jvg)
        analysis = self.l3.analyze_state(doc_id)
        return {"status": "success", "doc_id": doc_id, "jvg": jvg, "audit": audit, "analysis": analysis}

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return self.l2.search(query, top_k=top_k)

    def execute_step(self, doc_id: str, new_state: str = None, action_result: str = None) -> Dict[str, Any]:
        return self.l4.step(doc_id, new_state, action_result)

    def explain(self, doc_id: str) -> str:
        jvg = self.l2.get(doc_id)
        if not jvg:
            return "Документ не найден"
        return self.l5.explain(doc_id, jvg)


def test_cognitive_os():
    os = CognitiveOS(storage_dir="test_os_store", vector_db_path="test_os_vectors")
    print("=== Тест 1: Событие ===")
    event = {
        "title": "Системный сбой",
        "entity": "сервер",
        "source": "мониторинг",
        "purpose": "восстановление работы",
        "actions": ["проверить логи", "перезапустить сервис"]
    }
    result = os.process_event(event)
    print(f"Документ создан: {result['doc_id']}")
    print(f"Аудит: {result['audit']['valid']}")
    print(f"Анализ: {result['analysis']}")

    print("\n=== Тест 2: Текст ===")
    text = """
entity:
  name: Тестовая система
  type: система
  purpose: проверка Cognitive OS
state:
  current: ИССЛЕДОВАНИЕ
actions:
  next_steps: протестировать, развернуть
"""
    result = os.process_text(text)
    print(f"Документ создан: {result['doc_id']}")
    print(f"Анализ: {result['analysis']}")

    print("\n=== Тест 3: Поиск ===")
    results = os.search("система сбой")
    for r in results:
        print(f"  {r.get('title', '')} — {r.get('type', '')}")

if __name__ == "__main__":
    test_cognitive_os()
