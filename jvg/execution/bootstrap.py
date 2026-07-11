from .registry import ExecutorRegistry
from .executors.cmd import CmdExecutor
from .executors.powershell import PowerShellExecutor
from .executors.url import UrlExecutor
from .executors.rollback import RollbackExecutor
from .executors.http import HttpExecutor
from .executors.telegram import TelegramExecutor
from .executors.git import GitExecutor
from ..security import SecurityEngine, RiskLevel

def register_all():
    ExecutorRegistry.register("run_cmd", CmdExecutor())
    ExecutorRegistry.register("run_powershell", PowerShellExecutor())
    ExecutorRegistry.register("open_url", UrlExecutor())
    ExecutorRegistry.register("rollback", RollbackExecutor())
    ExecutorRegistry.register("http_request", HttpExecutor())
    ExecutorRegistry.register("send_telegram", TelegramExecutor())
    ExecutorRegistry.register("run_git", GitExecutor())
    
    # Разрешаем Git в политике безопасности
    security = SecurityEngine()
    security.allow("run_git", risk=RiskLevel.MEDIUM)
    security.allow("send_telegram", risk=RiskLevel.MEDIUM)
