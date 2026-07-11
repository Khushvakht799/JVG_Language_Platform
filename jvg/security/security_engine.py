"""
jvg/security/security_engine.py — Движок безопасности
"""

from typing import Dict, Any, List, Optional
from enum import Enum

class RiskLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEngine:
    def __init__(self):
        self.policies = {
            "http_request": {"risk": RiskLevel.SAFE, "allowed": True},
            "open_url": {"risk": RiskLevel.SAFE, "allowed": True},
            "run_powershell": {"risk": RiskLevel.MEDIUM, "allowed": True},
            "run_cmd": {"risk": RiskLevel.MEDIUM, "allowed": True},
        }
        
        self.blocked_patterns = [
            "rm -rf /",
            "format",
            "diskpart",
            "shutdown",
            "Stop-Service",
            "Remove-Item",
            "del /f /s",
            "rd /s /q"
        ]
        
        self.allowed_paths = [
            "C:\\Users\\Usuario\\Documents\\Projects",
            "C:\\Users\\Usuario\\Documents\\JVG_Language_Platform"
        ]

    def check(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action not in self.policies:
            return {
                "allowed": False,
                "reason": f"Действие '{action}' не зарегистрировано в политике безопасности",
                "risk": RiskLevel.CRITICAL.value
            }

        policy = self.policies[action]
        if not policy["allowed"]:
            return {
                "allowed": False,
                "reason": f"Действие '{action}' запрещено политикой безопасности",
                "risk": policy["risk"].value
            }

        params_str = str(params).lower()
        for pattern in self.blocked_patterns:
            if pattern.lower() in params_str:
                return {
                    "allowed": False,
                    "reason": f"Обнаружен запрещённый паттерн: {pattern}",
                    "risk": RiskLevel.CRITICAL.value
                }

        if "command" in params:
            command = params["command"]
            import re
            paths = re.findall(r'[A-Za-z]:\\[^\s"]+', command)
            for path in paths:
                if not any(path.startswith(allowed) for allowed in self.allowed_paths):
                    return {
                        "allowed": False,
                        "reason": f"Путь '{path}' не входит в разрешённые области",
                        "risk": RiskLevel.HIGH.value
                    }

        return {
            "allowed": True,
            "risk": policy["risk"].value,
            "message": f"Действие '{action}' разрешено"
        }

    def allow(self, action: str, risk: RiskLevel = RiskLevel.MEDIUM):
        self.policies[action] = {"risk": risk, "allowed": True}

    def deny(self, action: str):
        if action in self.policies:
            self.policies[action]["allowed"] = False

    def add_blocked_pattern(self, pattern: str):
        self.blocked_patterns.append(pattern)

    def add_allowed_path(self, path: str):
        self.allowed_paths.append(path)
