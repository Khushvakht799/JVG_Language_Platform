"""
l4_execution.py — Слой исполнения L4
"""

import os
import sys
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, '03_runtime'))
from runtime import JVGRuntime

class L4Execution:
    def __init__(self, storage_dir: str = "jvg_store"):
        self.runtime = JVGRuntime(storage_dir=storage_dir)

    def step(self, doc_id: str, new_state: Optional[str] = None, action_result: Optional[str] = None) -> Dict[str, Any]:
        return self.runtime.step(doc_id, new_state, action_result)

    def run_sequence(self, doc_id: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.runtime.run(doc_id, steps)

    def get_state(self, doc_id: str) -> str:
        return self.runtime.get_state(doc_id)
