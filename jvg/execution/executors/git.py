"""
jvg/execution/executors/git.py — Git исполнитель с саморегистрацией
"""

import subprocess
import os
import time
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
            
            full_command = f"git {command}"
            print(f"   ⚡ Выполнение Git: {full_command}")
            
            start = time.time()
            process = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            duration = time.time() - start
            
            return ExecutionResult(
                success=process.returncode == 0,
                action=self.name,
                exit_code=process.returncode,
                stdout=process.stdout,
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
