from pathlib import Path

# Создаём папку jvg, если её нет
Path("jvg").mkdir(exist_ok=True)

# Содержимое __init__.py
content = '''\"\"\"
jvg — пакет JVG Language Platform
\"\"\"

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

__version__ = "1.0.0"
'''

# Записываем файл
with open("jvg/__init__.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ __init__.py создан")
print("   Папка: jvg/")
