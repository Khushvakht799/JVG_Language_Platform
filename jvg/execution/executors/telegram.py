"""
jvg/execution/executors/telegram.py — Telegram исполнитель с саморегистрацией
"""

import requests
import time
from typing import Dict, Any
from .base import BaseExecutor
from ..result import ExecutionResult
from ...security.security_engine_v2 import RiskLevel

class TelegramExecutor(BaseExecutor):
    name = "send_telegram"
    description = "Отправляет сообщение в Telegram"
    risk_level = RiskLevel.MEDIUM

    def validate(self, params: Dict[str, Any]) -> bool:
        return "message" in params and isinstance(params["message"], str)

    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        token = params.get("token", "")
        chat_id = params.get("chat_id", "")
        message = params.get("message", "")
        
        if not token or not chat_id:
            return ExecutionResult(
                success=False,
                action=self.name,
                error="Не указаны token или chat_id"
            )

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        start = time.time()
        try:
            response = requests.post(url, json=payload, timeout=10)
            duration = time.time() - start
            
            if response.status_code == 200:
                return ExecutionResult(
                    success=True,
                    action=self.name,
                    stdout=f"Сообщение отправлено в Telegram",
                    duration=duration,
                    data=response.json()
                )
            else:
                return ExecutionResult(
                    success=False,
                    action=self.name,
                    exit_code=response.status_code,
                    error=f"Ошибка Telegram API: {response.text}",
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
