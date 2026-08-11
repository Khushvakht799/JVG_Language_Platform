"""
jvg/models/world_model.py — Абстрактная модель мира
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class WorldModel(ABC):
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Получить текущее состояние"""
        pass
    
    @abstractmethod
    def apply_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Применить действие и вернуть новое состояние"""
        pass
