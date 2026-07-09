"""
jvg — JVG Language Platform
"""

from .core.config import Config
from .storage.store import JVGStore
from .runtime.runtime import JVGRuntime
from .execution.action_executor import ActionExecutor
from .execution.registry import ExecutorRegistry
from .execution.result import ExecutionResult
from .execution.logger import ExecutionLogger
from .execution.bootstrap import register_all

register_all()

__version__ = "2.0.0"
