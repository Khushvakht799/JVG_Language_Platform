from typing import Dict, Optional
from .executors.base import BaseExecutor

class ExecutorRegistry:
    _executors: Dict[str, BaseExecutor] = {}

    @classmethod
    def register(cls, name: str, executor: BaseExecutor):
        cls._executors[name] = executor

    @classmethod
    def get(cls, name: str) -> Optional[BaseExecutor]:
        return cls._executors.get(name)

    @classmethod
    def list(cls) -> list:
        return list(cls._executors.keys())

    @classmethod
    def clear(cls):
        cls._executors.clear()
