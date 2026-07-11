"""
fix_git_security.py — Добавляет Git в глобальную политику безопасности
"""

from jvg.execution.action_executor import _security
from jvg import RiskLevel

# Разрешаем Git в глобальном экземпляре
_security.allow("run_git", risk=RiskLevel.MEDIUM)
print("✅ run_git разрешён в глобальной политике")

# Проверяем
policy = _security.policies.get("run_git")
print(f"   Политика: {policy}")
