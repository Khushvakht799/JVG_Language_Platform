"""
test_library_import.py — Проверка импорта библиотеки
"""

from library import JVGLibrary

lib = JVGLibrary()
jvg = lib.system_template("Тест", "проверка")
print(f'✅ Импорт работает: {jvg["vectorograph"]["entity"]["name"]}')
