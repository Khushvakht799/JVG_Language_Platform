"""
jvg/execution/executors/url.py — URL исполнитель
"""

import webbrowser
import time
from typing import Dict, Any
from .base import BaseExecutor
from ..result import ExecutionResult

class UrlExecutor(BaseExecutor):
    name = "open_url"
    description = "Открывает URL в браузере"

    def validate(self, params: Dict[str, Any]) -> bool:
        return "url" in params and isinstance(params["url"], str)

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        url = params.get("url", "")
        start = time.time()
        try:
            webbrowser.open(url)
            duration = time.time() - start
            return ExecutionResult(
                success=True,
                action=self.name,
                stdout=f"URL открыт: {url}",
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
