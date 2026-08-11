"""
jvg/observers/fake_observer.py — Фейковый наблюдатель для тестов
"""

from .base import WorldObserver
from typing import Dict, Any

class FakeObserver(WorldObserver):
    def __init__(self, state: Dict[str, Any]):
        self.state = state.copy()
    
    def observe(self) -> Dict[str, Any]:
        """Вернуть заданное состояние"""
        return self.state.copy()
