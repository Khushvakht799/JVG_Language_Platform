"""
jvg/execution/interpreter.py — Semantic Interpreter
Превращает ExecutionResult в факты для FSM.
"""

from typing import Dict, Any
from .result import ExecutionResult

class SemanticInterpreter:
    @staticmethod
    def interpret(result: ExecutionResult) -> Dict[str, Any]:
        """
        Превращает результат выполнения в структурированные факты.
        """
        facts = {
            "success": result.success,
            "action": result.action,
            "timestamp": result.timestamp,
            "duration": result.duration,
            "error": result.error
        }

        # HTTP
        if result.action == "http_request" and result.exit_code is not None:
            facts["http"] = {
                "status_code": result.exit_code,
                "success": result.success,
                "body": result.stdout[:500] if result.stdout else None,
                "retry": result.exit_code in [503, 429, 502, 504],
                "auth_required": result.exit_code == 401,
                "not_found": result.exit_code == 404,
                "redirect": result.exit_code in [301, 302, 307, 308]
            }

        # CMD / PowerShell
        if result.action in ["run_cmd", "run_powershell"]:
            facts["execution"] = {
                "exit_code": result.exit_code,
                "success": result.success,
                "output": result.stdout,
                "error": result.stderr
            }

        # URL
        if result.action == "open_url":
            facts["browser"] = {
                "opened": result.success,
                "url": result.stdout.replace("URL открыт: ", "") if result.stdout else None
            }

        return facts
