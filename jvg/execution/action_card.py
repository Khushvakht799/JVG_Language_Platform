"""
jvg/execution/action_card.py — Карточка решения для действия
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ActionCard:
    action: str
    command: str
    goal: str = ""
    expected_result: str = ""
    side_effects: List[str] = field(default_factory=list)
    risk_score: int = 0
    reversible: bool = False
    affected_resources: List[str] = field(default_factory=list)
    requires_confirmation: bool = False
    allowed_by_policy: bool = False
    final_decision: str = "PENDING"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "command": self.command,
            "goal": self.goal,
            "expected_result": self.expected_result,
            "side_effects": self.side_effects,
            "risk_score": self.risk_score,
            "reversible": self.reversible,
            "affected_resources": self.affected_resources,
            "requires_confirmation": self.requires_confirmation,
            "allowed_by_policy": self.allowed_by_policy,
            "final_decision": self.final_decision,
            "timestamp": self.timestamp
        }

    def print_card(self):
        print("\n" + "="*50)
        print("📋 КАРТОЧКА РЕШЕНИЯ")
        print("="*50)
        print(f"Действие:    {self.action}")
        print(f"Команда:     {self.command}")
        print(f"Цель:        {self.goal or 'не указана'}")
        print(f"Результат:   {self.expected_result or 'не указан'}")
        print(f"Побочные эффекты: {', '.join(self.side_effects) if self.side_effects else 'нет'}")
        print(f"Риск:        {self.risk_score}/10")
        print(f"Обратимость: {'Да' if self.reversible else 'Нет'}")
        print(f"Ресурсы:     {', '.join(self.affected_resources) if self.affected_resources else 'не указаны'}")
        print(f"Подтверждение: {'Требуется' if self.requires_confirmation else 'Не требуется'}")
        print(f"Политика:    {'Разрешено' if self.allowed_by_policy else '❌ ЗАПРЕЩЕНО'}")
        print(f"Решение:     {self.final_decision}")
        print("="*50 + "\n")
