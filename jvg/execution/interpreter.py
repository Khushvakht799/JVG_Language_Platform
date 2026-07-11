"""
jvg/execution/interpreter.py — Универсальный интерпретатор (с актуальным состоянием Git)
"""

from typing import Dict, Any
from .result import ExecutionResult
from .git_interpreter import GitInterpreter

class SemanticInterpreter:
    @staticmethod
    def interpret(result: ExecutionResult, repo_path: str = ".") -> Dict[str, Any]:
        facts = {
            "success": result.success,
            "action": result.action,
            "timestamp": result.timestamp,
            "duration": result.duration,
            "error": result.error
        }

        # HTTP интерпретация
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

        # Git интерпретация — всегда используем актуальное состояние
        if result.action == "run_git":
            # Получаем актуальное состояние репозитория
            git_facts = GitInterpreter.get_current_status(repo_path)
            facts.update(git_facts)
            # Добавляем информацию о выполненной команде
            facts["git_command"] = result.stdout[:100] if result.stdout else ""

        # CMD / PowerShell интерпретация
        if result.action in ["run_cmd", "run_powershell"]:
            facts["execution"] = {
                "exit_code": result.exit_code,
                "success": result.success,
                "output": result.stdout,
                "error": result.stderr
            }

        # URL интерпретация
        if result.action == "open_url":
            facts["browser"] = {
                "opened": result.success,
                "url": result.stdout.replace("URL открыт: ", "") if result.stdout else None
            }

        return facts
