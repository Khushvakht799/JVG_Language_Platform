"""
fix_security_policy.py — Добавляет Telegram в политику безопасности
"""

from jvg import SecurityEngine, RiskLevel

# Получаем экземпляр Security Engine
security = SecurityEngine()

# Разрешаем Telegram
security.allow("send_telegram", risk=RiskLevel.MEDIUM)
print("✅ send_telegram разрешён в политике безопасности")

# Проверяем
policy = security.policies.get("send_telegram")
print(f"   Политика: {policy}")
