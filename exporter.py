"""
exporter.py — Экспорт JVG в исполнимые форматы
BPMN, UML, State Machine, JSON Schema.
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from datetime import datetime

class JVGExporter:
    """Экспорт JVG в различные форматы."""
    
    def to_json_schema(self, jvg: Dict[str, Any]) -> Dict[str, Any]:
        """Экспортирует структуру JVG в JSON Schema."""
        data = jvg.get("vectorograph", {})
        entity = data.get("entity", {})
        
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "vectorograph": {
                    "type": "object",
                    "properties": {
                        "meta": {
                            "type": "object",
                            "properties": {
                                "version": {"type": "string"},
                                "title": {"type": "string"},
                                "date": {"type": "string"},
                                "author": {"type": "string"},
                                "status": {"type": "string", "enum": ["черновик", "готово", "уточняется"]}
                            },
                            "required": ["version", "title"]
                        },
                        "entity": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string", "enum": ["система", "процесс", "идея", "агент"]},
                                "purpose": {"type": "string"}
                            },
                            "required": ["name", "type", "purpose"]
                        }
                    }
                }
            }
        }
        return schema
    
    def to_bpmn(self, jvg: Dict[str, Any]) -> str:
        """Экспортирует процесс в BPMN (XML)."""
        data = jvg.get("vectorograph", {})
        entity = data.get("entity", {})
        actions = data.get("actions", {})
        
        root = ET.Element("definitions", xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL")
        process = ET.SubElement(root, "process", id=entity.get("name", "process"), isExecutable="true")
        
        # Стартовое событие
        start = ET.SubElement(process, "startEvent", id="StartEvent")
        
        # Шаги как задачи
        for i, step in enumerate(actions.get("next_steps", [])):
            task = ET.SubElement(process, "task", id=f"Task_{i}", name=step)
            if i == 0:
                ET.SubElement(process, "sequenceFlow", id=f"Flow_{i}", sourceRef="StartEvent", targetRef=f"Task_{i}")
            else:
                ET.SubElement(process, "sequenceFlow", id=f"Flow_{i}", sourceRef=f"Task_{i-1}", targetRef=f"Task_{i}")
        
        # Конечное событие
        end = ET.SubElement(process, "endEvent", id="EndEvent")
        if actions.get("next_steps"):
            last_idx = len(actions.get("next_steps", [])) - 1
            ET.SubElement(process, "sequenceFlow", id="Flow_end", sourceRef=f"Task_{last_idx}", targetRef="EndEvent")
        else:
            ET.SubElement(process, "sequenceFlow", id="Flow_end", sourceRef="StartEvent", targetRef="EndEvent")
        
        return ET.tostring(root, encoding="unicode", method="xml")
    
    def to_uml(self, jvg: Dict[str, Any]) -> str:
        """Экспортирует сущность в UML (PlantUML)."""
        data = jvg.get("vectorograph", {})
        entity = data.get("entity", {})
        structure = data.get("structure", {})
        
        lines = ["@startuml"]
        lines.append(f"class {entity.get('name', 'Entity')} {{")
        lines.append(f"  + имя: {entity.get('name', '')}")
        lines.append(f"  + тип: {entity.get('type', '')}")
        lines.append(f"  + назначение: {entity.get('purpose', '')}")
        for comp in structure.get("components", []):
            lines.append(f"  + компонент: {comp}")
        lines.append("}")
        
        if structure.get("layers"):
            lines.append(f"class {entity.get('name', 'Entity')}Layers {{")
            for layer in structure.get("layers", []):
                lines.append(f"  + слой: {layer}")
            lines.append("}")
            lines.append(f"{entity.get('name', 'Entity')} --> {entity.get('name', 'Entity')}Layers")
        
        lines.append("@enduml")
        return "\n".join(lines)
    
    def to_state_machine(self, jvg: Dict[str, Any]) -> str:
        """Экспортирует состояния в State Machine (Python)."""
        data = jvg.get("vectorograph", {})
        entity = data.get("entity", {})
        state_data = data.get("state", {})
        actions = data.get("actions", {})
        
        name = entity.get("name", "StateMachine")
        current = state_data.get("current", "IDLE")
        transitions = {
            "ИССЛЕДОВАНИЕ": ["ПРОЕКТИРОВАНИЕ", "ОТЛОЖЕНО"],
            "ПРОЕКТИРОВАНИЕ": ["ВЫПОЛНЕНИЕ", "ЗАБЛОКИРОВАНО", "ОТЛОЖЕНО"],
            "ВЫПОЛНЕНИЕ": ["ЗАВЕРШЕНО", "ЗАБЛОКИРОВАНО", "ОТЛОЖЕНО"],
            "ЗАБЛОКИРОВАНО": ["ВЫПОЛНЕНИЕ", "ОТЛОЖЕНО"],
            "ЗАВЕРШЕНО": [],
            "ОТЛОЖЕНО": ["ИССЛЕДОВАНИЕ", "ПРОЕКТИРОВАНИЕ", "ВЫПОЛНЕНИЕ"]
        }
        
        lines = [
            f"class {name}Machine:",
            f"    def __init__(self):",
            f"        self.state = '{current}'",
            "        self.history = []",
            ""
        ]
        
        for from_state, to_states in transitions.items():
            for to_state in to_states:
                lines.append(f"    def transition_{from_state}_to_{to_state.replace(' ', '_')}(self):")
                lines.append(f"        if self.state != '{from_state}':")
                lines.append(f"            raise ValueError(f'Недопустимый переход из {{self.state}}')")
                lines.append(f"        self.history.append(('{from_state}', '{to_state}'))")
                lines.append(f"        self.state = '{to_state}'")
                lines.append("")
        
        lines.append(f"    def next_steps(self):")
        lines.append(f"        return {actions.get('next_steps', [])}")
        
        return "\n".join(lines)


def test_exporter():
    print("=== Экспорт JVG ===")
    
    from library import JVGLibrary
    lib = JVGLibrary()
    jvg = lib.process_template("Тестовый процесс", "проверка экспорта")
    
    exporter = JVGExporter()
    
    print("\n1. JSON Schema:")
    print(json.dumps(exporter.to_json_schema(jvg), indent=2, ensure_ascii=False)[:200] + "...")
    
    print("\n2. BPMN (XML):")
    print(exporter.to_bpmn(jvg)[:200] + "...")
    
    print("\n3. UML (PlantUML):")
    print(exporter.to_uml(jvg))
    
    print("\n4. State Machine (Python):")
    print(exporter.to_state_machine(jvg))


if __name__ == "__main__":
    test_exporter()
