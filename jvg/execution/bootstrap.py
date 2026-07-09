from .registry import ExecutorRegistry
from .executors.cmd import CmdExecutor
from .executors.powershell import PowerShellExecutor
from .executors.url import UrlExecutor
from .executors.rollback import RollbackExecutor

def register_all():
    ExecutorRegistry.register("run_cmd", CmdExecutor())
    ExecutorRegistry.register("run_powershell", PowerShellExecutor())
    ExecutorRegistry.register("open_url", UrlExecutor())
    ExecutorRegistry.register("rollback", RollbackExecutor())
