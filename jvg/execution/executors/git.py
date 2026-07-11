"""
jvg/execution/executors/git.py — Git исполнитель (улучшенный)
"""

import subprocess
import os
import time
import shlex
from typing import Dict, Any
from .base import BaseExecutor
from ..result import ExecutionResult
from ...security.security_engine_v2 import RiskLevel

class GitExecutor(BaseExecutor):
    name = "run_git"
    description = "Выполняет Git-команды"
    risk_level = RiskLevel.MEDIUM

    def validate(self, params: Dict[str, Any]) -> bool:
        return "command" in params and isinstance(params["command"], str)

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        command = params.get("command", "")
        repo_path = params.get("repo_path", ".")
        timeout = params.get("timeout", 30)

        original_dir = os.getcwd()
        
        try:
            if repo_path != ".":
                os.chdir(repo_path)
            
            # Безопасный запуск без shell=True
            args = ["git"] + shlex.split(command)
            print(f"   ⚡ Выполнение Git: {' '.join(args)}")
            
            start = time.time()
            process = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            duration = time.time() - start
            
            # Объединяем вывод для удобства
            output = process.stdout
            if process.stderr:
                output += "\n" + process.stderr
            
            success = process.returncode == 0
            
            return ExecutionResult(
                success=success,
                action=self.name,
                exit_code=process.returncode,
                stdout=output.strip(),
                stderr=process.stderr,
                duration=duration
            )
        except subprocess.TimeoutExpired:
            duration = time.time() - start
            return ExecutionResult(
                success=False,
                action=self.name,
                exit_code=-1,
                error=f"Timeout after {timeout}s",
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start
            return ExecutionResult(
                success=False,
                action=self.name,
                exit_code=-1,
                error=str(e),
                duration=duration
            )
        finally:
            os.chdir(original_dir)
