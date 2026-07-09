#!/usr/bin/env python
"""
tools.py — Единый управляющий инструмент JVG Platform
"""

import sys
import os
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
            "list": self.list_docs,
            "run": self.run_doc,
            "graph": self.graph,
            "purge": self.purge,
        }

    def run(self, args):
        if len(args) < 2:
            self.print_help()
            return

        cmd = args[1]
        cmd_args = args[2:] if len(args) > 2 else []

        if cmd in self.commands:
            self.commands[cmd](cmd_args)
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
    list         — показать все документы в хранилище
    run          — активировать правила для документа
    graph        — сгенерировать граф связей
    purge        — полная очистка платформы

Примеры:
    python tools.py doctor
    python tools.py list
    python tools.py run "Перезапуск Explorer"
    python tools.py graph
    python tools.py purge
""")

    # === Команды ===

    def migrate(self, args):
        print("🔄 Запуск миграции...")
        self._run_script("migrate", "migrate.py", args)

    def rebuild(self, args):
        print("🔨 Пересборка индексов...")
        self._run_script("bootstrap", "rebuild.py", args)

    def doctor(self, args):
        print("🩺 Диагностика системы...")
        self._run_script("utils", "doctor.py", args)

    def repair(self, args):
        print("🔧 Восстановление данных...")
        self._run_script("repair", "repair.py", args)

    def benchmark(self, args):
        print("📊 Замер производительности...")
        self._run_script("dev", "benchmark.py", args)

    def clean(self, args):
        print("🧹 Очистка...")
        self._run_script("utils", "clean.py", args)

    def bootstrap(self, args):
        print("🚀 Первичная настройка...")
        self._run_script("bootstrap", "bootstrap.py", args)

    def version(self, args):
        print("JVG Platform v1.0.0")

    def purge(self, args):
        """Полная очистка платформы."""
        print("🗑️ Запуск полной очистки...")
        subprocess.run([sys.executable, "purge.py"])

    def list_docs(self, args):
        """Показывает все документы в хранилище."""
        print("📁 Документы в хранилище:")
        sys.path.insert(0, str(BASE_DIR))
        from jvg import JVGStore
        store = JVGStore()
        items = store.list()
        if not items:
            print("   (пусто)")
            return
        for i, item in enumerate(items, 1):
            title = item.get("title", "без названия")
            doc_id = item.get("id", "unknown")
            doc_type = item.get("type", "unknown")
            state = "unknown"
            jvg = store.get(doc_id)
            if jvg:
                state = jvg.get("vectorograph", {}).get("state", {}).get("current", "unknown")
            print(f"   {i}. {title} ({doc_type}) — {doc_id[:30]}... [{state}]")

    def run_doc(self, args):
        """Активирует правила для документа."""
        if not args:
            print("❌ Укажите название или ID документа")
            print("   Пример: python tools.py run 'Перезапуск Explorer'")
            return

        query = " ".join(args)
        print(f"🔍 Поиск документа: {query}")

        sys.path.insert(0, str(BASE_DIR))
        from jvg_runtime import IntegratedRuntime
        from jvg import JVGStore

        store = JVGStore()
        runtime = IntegratedRuntime(debug=True)

        doc_id = None
        for item in store.list():
            if query.lower() in item.get("title", "").lower() or query == item.get("id", ""):
                doc_id = item["id"]
                break

        if not doc_id:
            print(f"❌ Документ не найден: {query}")
            return

        print(f"✅ Документ найден: {doc_id}")

        jvg = store.get(doc_id)
        current_state = jvg.get("vectorograph", {}).get("state", {}).get("current", "")
        print(f"📊 Текущее состояние: {current_state}")

        if current_state != "НЕСТАБИЛЬНО":
            print(f"🔄 Перевод в состояние НЕСТАБИЛЬНО...")
            result = runtime.step(doc_id, "НЕСТАБИЛЬНО", "Активация правил через tools.py")
            print(f"Результат: {result}")
        else:
            print("ℹ️ Документ уже в состоянии НЕСТАБИЛЬНО")

    def graph(self, args):
        """Генерирует граф связей."""
        print("📊 Генерация графа...")
        sys.path.insert(0, str(BASE_DIR))
        from visualizer import JVGVisualizer
        from jvg import JVGStore
        store = JVGStore()
        visualizer = JVGVisualizer()
        output = visualizer.visualize_store(store, title="JVG Platform Graph", output_file="platform_graph")
        if output:
            print(f"✅ Граф сохранён: {output}")

    def _run_script(self, subdir, script, args):
        script_path = TOOLS_DIR / subdir / script
        if not script_path.exists():
            print(f"❌ Скрипт не найден: {script_path}")
            return

        cmd = [sys.executable, str(script_path)] + args
        subprocess.run(cmd)


if __name__ == "__main__":
    tools = JVGTools()
    tools.run(sys.argv)
