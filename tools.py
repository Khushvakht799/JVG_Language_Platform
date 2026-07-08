#!/usr/bin/env python
"""
tools.py — Единый управляющий инструмент JVG Platform
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
TOOLS_DIR = BASE_DIR / "tools"


class JVGTools:
    def __init__(self):
        self.commands = {
            "migrate": self.migrate,
            "rebuild": self.rebuild,
            "doctor": self.doctor,
            "repair": self.repair,
            "benchmark": self.benchmark,
            "clean": self.clean,
            "bootstrap": self.bootstrap,
            "version": self.version,
        }

    def run(self, args):
        if len(args) < 2:
            self.print_help()
            return

        cmd = args[1]
        if cmd in self.commands:
            self.commands[cmd](args[2:])
        else:
            print(f"❌ Неизвестная команда: {cmd}")
            self.print_help()

    def print_help(self):
        print("""
JVG Tools — Единый управляющий инструмент

Использование:
    python tools.py <команда> [аргументы]

Команды:
    migrate      — миграция данных (идентичность, хранилище, Chroma)
    rebuild      — полная пересборка индексов
    doctor       — диагностика системы
    repair       — восстановление повреждённых данных
    benchmark    — замер производительности
    clean        — очистка временных файлов
    bootstrap    — первичная настройка
    version      — версия платформы

Примеры:
    python tools.py doctor
    python tools.py migrate --identity
    python tools.py rebuild --chroma
    python tools.py clean --all
""")

    # === Команды ===

    def migrate(self, args):
        """Запускает миграцию."""
        print("🔄 Запуск миграции...")
        self._run_script("migrate", "migrate.py", args)

    def rebuild(self, args):
        """Пересборка индексов."""
        print("🔨 Пересборка индексов...")
        self._run_script("bootstrap", "rebuild.py", args)

    def doctor(self, args):
        """Диагностика."""
        print("🩺 Диагностика системы...")
        self._run_script("utils", "doctor.py", args)

    def repair(self, args):
        """Восстановление."""
        print("🔧 Восстановление данных...")
        self._run_script("repair", "repair.py", args)

    def benchmark(self, args):
        """Замер производительности."""
        print("📊 Замер производительности...")
        self._run_script("dev", "benchmark.py", args)

    def clean(self, args):
        """Очистка."""
        print("🧹 Очистка...")
        self._run_script("utils", "clean.py", args)

    def bootstrap(self, args):
        """Первичная настройка."""
        print("🚀 Первичная настройка...")
        self._run_script("bootstrap", "bootstrap.py", args)

    def version(self, args):
        """Версия."""
        try:
            with open(BASE_DIR / "jvg" / "__init__.py", "r") as f:
                for line in f:
                    if "__version__" in line:
                        print(line.strip())
                        return
        except:
            pass
        print("JVG Platform v1.0.0")

    def _run_script(self, subdir, script, args):
        """Запускает скрипт из подпапки tools/."""
        script_path = TOOLS_DIR / subdir / script
        if not script_path.exists():
            print(f"❌ Скрипт не найден: {script_path}")
            return

        cmd = [sys.executable, str(script_path)] + args
        subprocess.run(cmd)


if __name__ == "__main__":
    tools = JVGTools()
    tools.run(sys.argv)
