import subprocess
import time
from typing import Dict, Any
from .base import BaseExecutor
from ..result import ExecutionResult

class CmdExecutor(BaseExecutor):
    name = "run_cmd"
    description = "Выполняет команду в cmd.exe"

    def validate(self, params: Dict[str, Any]) -> bool:
        return "command" in params and isinstance(params["command"], str)

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        command = params.get("command", "")
        timeout = params.get("timeout", 30)

        start = time.time()
        try:
            process = subprocess.run(
                command,
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
