"""
fix_tools_import.py — Исправляет импорт store в tools.py
"""

import os
import re

with open("tools.py", "r", encoding="utf-8") as f:
    content = f.read()

# Заменяем импорт store на jvg.store
content = content.replace(
    "from store import JVGStore",
    "from jvg.store import JVGStore"
)

with open("tools.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ tools.py исправлен: импорт store → jvg.store")
