"""
jvg/execution/executors/http.py — Настоящий HTTP исполнитель
"""

import requests
import time
from typing import Dict, Any
from .base import BaseExecutor
from ..result import ExecutionResult

class HttpExecutor(BaseExecutor):
    name = "http_request"
    description = "Выполняет реальный HTTP-запрос"

    def validate(self, params: Dict[str, Any]) -> bool:
        return "url" in params and isinstance(params["url"], str)

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        url = params.get("url")
        method = params.get("method", "GET").upper()
        headers = params.get("headers", {})
        body = params.get("body", {})
        timeout = params.get("timeout", 10)

        start = time.time()
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, json=body, headers=headers, timeout=timeout)
            elif method == "PUT":
                response = requests.put(url, json=body, headers=headers, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                return ExecutionResult(
                    success=False,
                    action=self.name,
                    error=f"Неподдерживаемый метод: {method}"
                )

            duration = time.time() - start
            return ExecutionResult(
                success=200 <= response.status_code < 300,
                action=self.name,
                exit_code=response.status_code,
                stdout=response.text[:1000],
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
