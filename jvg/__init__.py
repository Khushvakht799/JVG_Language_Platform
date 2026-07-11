"""
jvg — JVG Language Platform
"""

from .core.config import Config
from .storage.store import JVGStore
from .runtime.runtime import JVGRuntime
from .runtime.executor import JVGExecutor
from .execution.action_executor import ActionExecutor
from .execution.registry import ExecutorRegistry
from .execution.result import ExecutionResult
from .execution.logger import ExecutionLogger
from .execution.bootstrap import register_all
from .events.event_bus import EventBus
from .planning.goal_engine import GoalEngine
from .planning.goal_planner import GoalPlanner
from .planning.router import Router
from .security.security_engine import SecurityEngine, RiskLevel
from .security.simulation_engine import SimulationEngine
from .security.security_engine_v2 import SecurityEngineV2
from .agents.agent_runner import AgentRunner

register_all()

__version__ = "2.0.0"
