from abc import ABC, abstractmethod
from typing import Dict, Any
from ..result import ExecutionResult

class BaseExecutor(ABC):
    name: str = "base"
    description: str = "Базовый исполнитель"

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
