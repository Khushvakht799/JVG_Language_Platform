"""
preference.py — Модуль Preference Profile для JVG
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class PreferenceProfile:
    """Профиль предпочтений пользователя/проекта/агента."""
    
    # Базовые предпочтения (по умолчанию — нейтральные)
    Practicality: float = 0.50           # практичность
    TimePriority: float = 0.50           # приоритет времени
    ResourceEfficiency: float = 0.50     # эффективность ресурсов
    ImplementationFocus: float = 0.50    # ориентация на реализацию
    AbstractionTolerance: float = 0.50   # допустимый уровень абстракции
    AutomationPreference: float = 0.50   # предпочтение автоматизации
    RiskTolerance: float = 0.50          # толерантность к риску
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "Practicality": self.Practicality,
            "TimePriority": self.TimePriority,
            "ResourceEfficiency": self.ResourceEfficiency,
            "ImplementationFocus": self.ImplementationFocus,
            "AbstractionTolerance": self.AbstractionTolerance,
            "AutomationPreference": self.AutomationPreference,
            "RiskTolerance": self.RiskTolerance
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'PreferenceProfile':
        return cls(**data)
    
    @classmethod
    def load(cls, path: str = "preference_profile.json") -> 'PreferenceProfile':
        """Загружает профиль из файла."""
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        return cls()  # возвращаем нейтральный профиль
    
    def save(self, path: str = "preference_profile.json"):
        """Сохраняет профиль в файл."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# Профиль по умолчанию для архитектора (твой)
ARCHITECT_PROFILE = PreferenceProfile(
    Practicality=0.98,
    TimePriority=0.90,
    ResourceEfficiency=0.95,
    ImplementationFocus=0.97,
    AbstractionTolerance=0.15,
    AutomationPreference=0.95,
    RiskTolerance=0.30
)

# Профиль по умолчанию для исследователя
RESEARCHER_PROFILE = PreferenceProfile(
    Practicality=0.40,
    TimePriority=0.30,
    ResourceEfficiency=0.50,
    ImplementationFocus=0.20,
    AbstractionTolerance=0.95,
    AutomationPreference=0.30,
    RiskTolerance=0.85
)


def get_preference_vector(profile: PreferenceProfile) -> list:
    """Превращает профиль в вектор для ранжирования."""
    return list(profile.to_dict().values())
