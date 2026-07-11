"""
jvg/execution/action_executor.py — Универсальный диспетчер (без политик)
"""

from typing import Dict, Any, Optional
from .registry import ExecutorRegistry
from .result import ExecutionResult
from .logger import ExecutionLogger
from .action_card import ActionCard
from ..security.security_engine_v2 import SecurityEngineV2
from ..security.simulation_engine import SimulationEngine

_security = SecurityEngineV2()
_simulator = SimulationEngine()

class ActionExecutor:
    @staticmethod
    def execute(action: str, params: Dict[str, Any], doc_id: Optional[str] = None, dry_run: bool = False) -> ExecutionResult:
        command = params.get("command", "")
        
        # Проверка через SecurityEngineV2
        check = _security.check(action, params)
        
        # Создаём карточку решения
        card = ActionCard(
            action=action,
            command=command,
            goal=params.get("goal", ""),
            expected_result=params.get("expected", ""),
            risk_score=check.get("risk_score", 0),
            reversible=not any(p in command.lower() for p in ["del", "remove", "format", "rd"]),
            affected_resources=_simulator._find_file_operations(command),
            side_effects=check.get("message", ""),
            requires_confirmation=check.get("risk_score", 0) > 5
        )

        card.allowed_by_policy = check["final_decision"] == "ALLOWED"
        card.final_decision = check["final_decision"]
        card.risk_score = check.get("risk_score", 0)
        card.side_effects = [check.get("message", "")] if check.get("message") else []

        card.print_card()

        if check["final_decision"] != "ALLOWED":
            return ExecutionResult(
                success=False,
                action=action,
                error=f"Безопасность: {check['message']}",
                exit_code=403
            )

        if dry_run:
            return ExecutionResult(
                success=True,
                action=action,
                stdout="DRY RUN: действие симулировано",
                data=card.to_dict()
            )

        executor = ExecutorRegistry.get(action)
        if not executor:
            return ExecutionResult(
                success=False,
                action=action,
                error=f"Неизвестный исполнитель: {action}"
            )

        result = executor.execute(params)
        if doc_id:
            ExecutionLogger.log(doc_id, action, result, params)
        return result
