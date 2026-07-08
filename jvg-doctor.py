"""
jvg-doctor — Диагностика проекта JVG
Проверяет импорты, структуру и зависимости.
"""

import os
import sys
import subprocess
from typing import List, Dict, Any

class JVGDoctor:
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.errors = []
        self.warnings = []

    def run(self) -> Dict[str, Any]:
        self.check_imports()
        self.check_structure()
        self.check_requirements()
        return {
            "status": "ok" if not self.errors else "error",
            "errors": self.errors,
            "warnings": self.warnings
        }

    def check_imports(self):
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith(".py") and file != "__init__.py" and not file.startswith("test_"):
                    self._check_file(os.path.join(root, file))

    def _check_file(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if "Dict[" in content and "from typing" not in content:
            self.errors.append(f"{filepath}: используется Dict, но нет импорта из typing")
        if "List[" in content and "from typing" not in content:
            self.errors.append(f"{filepath}: используется List, но нет импорта из typing")
        if "Optional[" in content and "from typing" not in content:
            self.errors.append(f"{filepath}: используется Optional, но нет импорта из typing")
        if "Any" in content and "from typing" not in content:
            if "Any" not in content.split("from typing")[0]:
                self.errors.append(f"{filepath}: используется Any, но нет импорта из typing")

    def check_structure(self):
        required_dirs = ["01_toolchain", "02_search", "03_runtime"]
        for d in required_dirs:
            if not os.path.exists(os.path.join(self.root_dir, d)):
                self.warnings.append(f"Отсутствует папка: {d}")

    def check_requirements(self):
        try:
            import chromadb
        except ImportError:
            self.warnings.append("chromadb не установлена")
        try:
            import sentence_transformers
        except ImportError:
            self.warnings.append("sentence-transformers не установлена")

def main():
    doctor = JVGDoctor()
    result = doctor.run()
    print(f"=== JVG Doctor ===")
    print(f"Статус: {result['status']}")
    if result['errors']:
        print("\n❌ Ошибки:")
        for e in result['errors']:
            print(f"  {e}")
    if result['warnings']:
        print("\n⚠️ Предупреждения:")
        for w in result['warnings']:
            print(f"  {w}")
    if not result['errors'] and not result['warnings']:
        print("✅ Всё чисто!")

if __name__ == "__main__":
    main()
