"""
jvg/execution/executors/rollback.py — Rollback для исполнителей
"""

from typing import Dict, Any
from .base import BaseExecutor
from ..result import ExecutionResult

class RollbackExecutor(BaseExecutor):
    name = "rollback"
    description = "Откат последнего действия"

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        action = params.get("action", "")
        if action == "run_cmd":
            return ExecutionResult(
                success=True,
                action="rollback_run_cmd",
                stdout="Откат CMD команды (заглушка)"
            )
        elif action == "run_powershell":
            return ExecutionResult(
                success=True,
                action="rollback_run_powershell",
                stdout="Откат PowerShell команды (заглушка)"
            )
        elif action == "open_url":
            return ExecutionResult(
                success=True,
                action="rollback_open_url",
                stdout="Откат открытия URL (заглушка)"
            )
        else:
            return ExecutionResult(
                success=False,
                action=f"rollback_{action}",
                error=f"Rollback для {action} не реализован"
            )
