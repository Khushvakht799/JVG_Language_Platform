"""
jvg/observers/base.py — Базовый интерфейс наблюдателя
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class WorldObserver(ABC):
    @abstractmethod
    def observe(self) -> Dict[str, Any]:
        """Получить текущее состояние мира"""
        pass
