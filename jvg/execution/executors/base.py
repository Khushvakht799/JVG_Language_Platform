"""
jvg/execution/executors/base.py — Базовый исполнитель с регистрацией политики
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..result import ExecutionResult
from ...security.security_engine_v2 import SecurityEngineV2, RiskLevel

class BaseExecutor(ABC):
    name: str = "base"
    description: str = "Базовый исполнитель"
    risk_level: RiskLevel = RiskLevel.MEDIUM
    allowed_paths: list = []

    def __init__(self):
        self._register_policy()

    def _register_policy(self):
        """Регистрирует политику безопасности для исполнителя."""
        security = SecurityEngineV2()
        security.allow(self.name, risk=self.risk_level)
        for path in self.allowed_paths:
            security.add_allowed_path(path)
        print(f"🔒 Политика зарегистрирована: {self.name} (риск: {self.risk_level.value})")

    def validate(self, params: Dict[str, Any]) -> bool:
        return True

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> ExecutionResult:
        pass

    def rollback(self, params: Dict[str, Any]) -> ExecutionResult:
        return ExecutionResult(
            success=True,
            action=f"rollback_{self.name}",
            stdout="Откат не реализован"
        )
