from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

@dataclass
class ExecutionResult:
    success: bool
    action: str
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    duration: Optional[float] = None
    timestamp: str = None
    data: Any = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "action": self.action,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration": self.duration,
            "timestamp": self.timestamp,
            "error": self.error
        }
