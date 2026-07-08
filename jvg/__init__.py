"""
jvg — пакет JVG Language Platform
"""

from .compiler import JVGCompiler
from .validator import JVGValidatorPipeline
from .store import JVGStore
from .vectorizer import JVGVectorizer
from .ranking import JVGRankingEngine
from .runtime import JVGRuntime
from .l1_adapter import L1Adapter
from .l2_memory import L2Memory
from .l3_models import L3Models
from .l4_execution import L4Execution
from .l5_audit import L5Audit
from .config import JVG_STORE_PATH, CHROMA_DB_PATH
from .preference import PreferenceProfile, ARCHITECT_PROFILE
from .metrics import MetricsCollector
from .feedback_engine import FeedbackEngine
from .identity import IdentityRegistry, UID, VersionedObject, generate_uid

__version__ = "1.0.0"
