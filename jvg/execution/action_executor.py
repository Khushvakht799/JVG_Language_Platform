"""
jvg/execution/action_executor.py — Диспетчер с логированием
"""

from typing import Dict, Any, Optional
from .registry import ExecutorRegistry
from .result import ExecutionResult
from .logger import ExecutionLogger

class ActionExecutor:
    @staticmethod
    def execute(action: str, params: Dict[str, Any], doc_id: Optional[str] = None) -> ExecutionResult:
        executor = ExecutorRegistry.get(action)
        if not executor:
            result = ExecutionResult(
                success=False,
                action=action,
                error=f"Неизвестный исполнитель: {action}"
            )
            if doc_id:
                ExecutionLogger.log(doc_id, action, result, params)
            return result

        result = executor.execute(params)
        if doc_id:
            ExecutionLogger.log(doc_id, action, result, params)
        return result
