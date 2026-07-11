"""
jvg/security/simulation_engine.py — Движок симуляции
"""

from typing import Dict, Any, List, Optional
import os
import re

class SimulationEngine:
    def __init__(self):
        self.safe_paths = [
            "C:\\Users\\Usuario\\Documents\\Projects",
            "C:\\Users\\Usuario\\Documents\\JVG_Language_Platform"
        ]

    def simulate(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Симулирует выполнение действия и возвращает прогноз изменений.
        """
        result = {
            "action": action,
            "params": params,
            "files_affected": [],
            "registry_affected": [],
            "processes_affected": [],
            "risk_score": 0,
            "can_rollback": False,
            "predicted_success": True,
            "warnings": []
        }

        if action == "run_cmd" or action == "run_powershell":
            command = params.get("command", "")
            result["files_affected"] = self._find_file_operations(command)
            result["registry_affected"] = self._find_registry_operations(command)
            result["processes_affected"] = self._find_process_operations(command)
            result["risk_score"] = self._calculate_risk(command)
            result["can_rollback"] = self._can_rollback(command)
            result["warnings"] = self._get_warnings(command)

        elif action == "http_request":
            url = params.get("url", "")
            result["warnings"] = self._check_url_safety(url)

        elif action == "delete_file":
            path = params.get("path", "")
            result["files_affected"] = [path]
            result["risk_score"] = 7
            result["can_rollback"] = False
            result["warnings"].append(f"Удаление файла: {path}")

        return result

    def _find_file_operations(self, command: str) -> List[str]:
        """Находит операции с файлами."""
        files = []
        patterns = [
            r'[A-Za-z]:\\[^\s"]+\.\w+',
            r'"[A-Za-z]:\\[^\s"]+\.\w+"',
        ]
        for pattern in patterns:
            files.extend(re.findall(pattern, command))
        return files

    def _find_registry_operations(self, command: str) -> List[str]:
        """Находит операции с реестром."""
        registry = []
        if "reg " in command.lower():
            registry.append("Реестр будет изменён")
        return registry

    def _find_process_operations(self, command: str) -> List[str]:
        """Находит операции с процессами."""
        processes = []
        if "taskkill" in command.lower():
            processes.append("Процессы будут завершены")
        if "start" in command.lower():
            processes.append("Новые процессы будут запущены")
        return processes

    def _calculate_risk(self, command: str) -> int:
        """Рассчитывает риск (0-10)."""
        risk = 0
        dangerous = [
            ("rm -rf", 10),
            ("format", 10),
            ("diskpart", 10),
            ("shutdown", 9),
            ("Stop-Service", 7),
            ("Remove-Item", 8),
            ("del /f /s", 8),
            ("rd /s /q", 8),
        ]
        for pattern, score in dangerous:
            if pattern in command.lower():
                risk = max(risk, score)
        return risk

    def _can_rollback(self, command: str) -> bool:
        """Проверяет, можно ли откатить действие."""
        if "echo" in command.lower():
            return True
        if "Write-Host" in command:
            return True
        return False

    def _get_warnings(self, command: str) -> List[str]:
        """Возвращает предупреждения."""
        warnings = []
        if "del" in command.lower() or "remove" in command.lower():
            warnings.append("Удаление файлов может быть необратимым")
        if "format" in command.lower():
            warnings.append("Форматирование диска приведёт к потере данных")
        if "shutdown" in command.lower():
            warnings.append("Выключение системы остановит все процессы")
        return warnings

    def _check_url_safety(self, url: str) -> List[str]:
        """Проверяет URL на безопасность."""
        warnings = []
        if "http://" in url and "localhost" not in url:
            warnings.append("Незащищённое соединение (HTTP)")
        return warnings
