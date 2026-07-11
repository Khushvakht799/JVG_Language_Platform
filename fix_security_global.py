"""
fix_security_global.py — Исправляет глобальную политику безопасности
"""

from jvg.execution.action_executor import _security
from jvg import RiskLevel

# Разрешаем send_telegram в глобальном экземпляре
_security.allow("send_telegram", risk=RiskLevel.MEDIUM)
print("✅ send_telegram разрешён в глобальной политике")

# Проверяем
policy = _security.policies.get("send_telegram")
print(f"   Политика: {policy}")
