"""
jvg/execution/logger.py — Логирование выполнения действий
"""

from datetime import datetime
from typing import Dict, Any
from ..storage.store import JVGStore
from .result import ExecutionResult

class ExecutionLogger:
    @staticmethod
    def log(doc_id: str, action: str, result: ExecutionResult, params: Dict[str, Any]):
        """
        Сохраняет запись о выполненном действии в хранилище.
        """
        store = JVGStore()
        
        # Создаём запись
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "doc_id": doc_id,
            "action": action,
            "params": params,
            "success": result.success,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": result.duration,
            "error": result.error
        }
        
        # Загружаем или создаём лог-документ
        log_doc_id = store.find_by_name("_execution_log")
        if log_doc_id:
            log_doc = store.get(log_doc_id)
        else:
            log_doc = {
                "vectorograph": {
                    "meta": {
                        "title": "Execution Log",
                        "type": "log",
                        "version": "1.0"
                    },
                    "entries": []
                }
            }
        
        log_doc["vectorograph"]["entries"].append(log_entry)
        
        if log_doc_id:
            store.update(log_doc_id, log_doc)
        else:
            store.create(log_doc)
        
        print(f"   📝 Лог сохранён: {action} -> {result.success}")
