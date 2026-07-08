"""
visualizer.py — Визуализация JVG через GraphViz
Строит графы связей между документами.
"""

import os
import json
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

class JVGVisualizer:
    def __init__(self, output_dir: str = "visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_dot(self, jvg_list: List[Dict[str, Any]], title: str = "JVG Graph") -> str:
        """
        Генерирует DOT-код для GraphViz на основе списка JVG.
        """
        dot_lines = [
            'digraph JVG {',
            '  rankdir=LR;',
            '  node [shape=box, style="rounded,filled", fillcolor=lightblue];',
            f'  label="{title}";',
            '  fontname="Arial";',
            '  labelloc=t;',
            ''
        ]

        nodes = {}
        edges = []

        for jvg in jvg_list:
            data = jvg.get("vectorograph", {})
            meta = data.get("meta", {})
            entity = data.get("entity", {})
            relations = data.get("relations", {})
            state = data.get("state", {})

            doc_id = meta.get("id", f"doc_{len(nodes)}")
            name = entity.get("name", "Без имени")
            node_type = entity.get("type", "unknown")
            status = state.get("current", "unknown")

            colors = {
                "система": "lightblue",
                "процесс": "lightgreen",
                "агент": "lightyellow",
                "идея": "lightpink"
            }
            color = colors.get(node_type, "lightgray")

            label = f"{name}\\n({node_type})\\n{status}"
            nodes[doc_id] = {
                "id": doc_id,
                "label": label,
                "color": color,
                "type": node_type,
                "status": status
            }

            for target in relations.get("connected_to", []):
                edges.append((doc_id, target, "связан"))

            for inp in relations.get("inputs", []):
                edges.append((doc_id, inp, "вход"))

            for out in relations.get("outputs", []):
                edges.append((out, doc_id, "выход"))

        for node_id, node_data in nodes.items():
            dot_lines.append(
                f'  "{node_id}" [label="{node_data["label"]}", fillcolor={node_data["color"]}];'
            )

        for source, target, label in edges:
            dot_lines.append(f'  "{source}" -> "{target}" [label="{label}"];')

        dot_lines.append('}')

        return "\n".join(dot_lines)

    def render(self, dot_code: str, output_file: str = "graph") -> str:
        """
        Рендерит DOT-код в изображение (PNG).
        Требует установленного GraphViz (dot).
        """
        dot_path = self.output_dir / f"{output_file}.dot"
        png_path = self.output_dir / f"{output_file}.png"

        with open(dot_path, 'w', encoding='utf-8') as f:
            f.write(dot_code)

        try:
            subprocess.run(
                ['dot', '-Tpng', str(dot_path), '-o', str(png_path)],
                check=True,
                capture_output=True,
                text=True
            )
            return str(png_path)
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка рендеринга: {e.stderr}")
            return str(dot_path)
        except FileNotFoundError:
            print("❌ GraphViz (dot) не установлен.")
            print("   Установите: winget install Graphviz.Graphviz")
            return str(dot_path)

    def visualize_store(self, store, title: str = "JVG Store Graph", output_file: str = "store_graph") -> str:
        """
        Визуализирует все документы из хранилища.
        """
        items = store.list()
        if not items:
            print("⚠️ Хранилище пусто")
            return ""

        jvgs = []
        for item in items:
            jvg = store.get(item["id"])
            if jvg:
                jvgs.append(jvg)

        dot = self.generate_dot(jvgs, title)
        return self.render(dot, output_file)


# ============================================================
# Тест
# ============================================================

def test_visualizer():
    print("=== Визуализация JVG ===")

    from library import JVGLibrary
    library = JVGLibrary()

    jvgs = [
        library.system_template("Сервер", "обработка данных", "тест"),
        library.process_template("Обновление", "обновление ПО", "тест"),
        library.agent_template("Монитор", "контроль состояния", "тест"),
        library.idea_template("Оптимизация", "ускорение работы", "тест")
    ]

    jvgs[0]["vectorograph"]["relations"]["connected_to"] = ["Сервер", "Монитор"]
    jvgs[1]["vectorograph"]["relations"]["connected_to"] = ["Сервер"]
    jvgs[2]["vectorograph"]["relations"]["connected_to"] = ["Сервер", "Оптимизация"]

    visualizer = JVGVisualizer()

    dot_code = visualizer.generate_dot(jvgs, "Тестовый граф JVG")
    print("✅ DOT-код сгенерирован")

    output = visualizer.render(dot_code, "test_graph")
    print(f"✅ Граф сохранён: {output}")

if __name__ == "__main__":
    test_visualizer()
