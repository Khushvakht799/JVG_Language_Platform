"""
jvg/security/security_engine_v2.py — Четырёхуровневый движок безопасности (без Registry)
"""

from typing import Dict, Any, List, Optional
from enum import Enum

class RiskLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEngineV2:
    def __init__(self):
        self.policies = {
            "http_request": {"risk": RiskLevel.SAFE, "allowed": True},
            "open_url": {"risk": RiskLevel.SAFE, "allowed": True},
            "run_powershell": {"risk": RiskLevel.MEDIUM, "allowed": True},
            "run_cmd": {"risk": RiskLevel.MEDIUM, "allowed": True},
            "send_telegram": {"risk": RiskLevel.MEDIUM, "allowed": True},
            "run_git": {"risk": RiskLevel.MEDIUM, "allowed": True},
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
        """
        Четырёхуровневая проверка без Registry.
        """
        result = {
            "action": action,
            "params": params,
            "executor_exists": True,  # Предполагаем, что исполнитель существует
            "executor_name": action,
            "policy_allowed": False,
            "policy_reason": "",
            "risk_score": 0,
            "risk_level": RiskLevel.SAFE.value,
            "blocked_pattern": None,
            "path_allowed": True,
            "path_reason": "",
            "final_decision": "PENDING",
            "message": ""
        }

        # Уровень 1: Проверка политики
        if action not in self.policies:
            result["final_decision"] = "POLICY_NOT_DEFINED"
            result["policy_reason"] = f"Действие '{action}' не зарегистрировано в политике безопасности"
            result["message"] = "Политика не определена"
            return result

        policy = self.policies[action]
        if not policy["allowed"]:
            result["final_decision"] = "POLICY_DENIED"
            result["policy_reason"] = f"Действие '{action}' запрещено политикой безопасности"
            result["message"] = "Запрещено политикой"
            return result

        result["policy_allowed"] = True
        result["risk_level"] = policy["risk"].value

        # Уровень 2: Проверка запрещённых паттернов
        params_str = str(params).lower()
        for pattern in self.blocked_patterns:
            if pattern.lower() in params_str:
                result["final_decision"] = "BLOCKED_PATTERN"
                result["blocked_pattern"] = pattern
                result["message"] = f"Обнаружен запрещённый паттерн: {pattern}"
                return result

        # Уровень 3: Проверка путей (если есть)
        if "command" in params:
            command = params["command"]
            import re
            paths = re.findall(r'[A-Za-z]:\\[^\s"]+', command)
            for path in paths:
                if not any(path.startswith(allowed) for allowed in self.allowed_paths):
                    result["final_decision"] = "PATH_DENIED"
                    result["path_allowed"] = False
                    result["path_reason"] = f"Путь '{path}' не входит в разрешённые области"
                    result["message"] = "Путь запрещён"
                    return result

        # Все проверки пройдены
        result["final_decision"] = "ALLOWED"
        result["message"] = f"Действие '{action}' разрешено"
        return result

    def allow(self, action: str, risk: RiskLevel = RiskLevel.MEDIUM):
        self.policies[action] = {"risk": risk, "allowed": True}

    def deny(self, action: str):
        if action in self.policies:
            self.policies[action]["allowed"] = False

    def add_blocked_pattern(self, pattern: str):
        self.blocked_patterns.append(pattern)

    def add_allowed_path(self, path: str):
        self.allowed_paths.append(path)
