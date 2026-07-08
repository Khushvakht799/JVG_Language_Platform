"""
ast_builder.py — Строитель семантического AST из CST
Превращает синтаксическое дерево (CST) в семантическое (AST).
"""

from typing import Dict, Any, List
from parser import ASTNode

class SemNode:
    """Базовый узел семантического AST."""
    def __init__(self, type: str, value: Any = None):
        self.type = type
        self.value = value
        self.children: List['SemNode'] = []

    def to_dict(self) -> Dict[str, Any]:
        """Превращает узел в словарь для JVG."""
        if self.type == "Meta":
            return self._meta_to_dict()
        elif self.type == "Entity":
            return self._entity_to_dict()
        elif self.type == "Context":
            return self._context_to_dict()
        elif self.type == "Structure":
            return self._structure_to_dict()
        elif self.type == "Relations":
            return self._relations_to_dict()
        elif self.type == "Logic":
            return self._logic_to_dict()
        elif self.type == "State":
            return self._state_to_dict()
        elif self.type == "Actions":
            return self._actions_to_dict()
        elif self.type == "Evolution":
            return self._evolution_to_dict()
        return {}

    def _meta_to_dict(self) -> Dict[str, Any]:
        return {
            "version": self._get_value("version", "1.0"),
            "title": self._get_value("title", ""),
            "date": self._get_value("date", ""),
            "author": self._get_value("author", ""),
            "status": self._get_value("status", "")
        }

    def _entity_to_dict(self) -> Dict[str, Any]:
        return {
            "name": self._get_value("name", ""),
            "type": self._get_value("type", ""),
            "purpose": self._get_value("purpose", "")
        }

    def _context_to_dict(self) -> Dict[str, Any]:
        return {
            "origin": self._get_value("origin", ""),
            "environment": self._get_value("environment", ""),
            "dependencies": self._get_list("dependencies")
        }

    def _structure_to_dict(self) -> Dict[str, Any]:
        return {
            "components": self._get_list("components"),
            "layers": self._get_list("layers")
        }

    def _relations_to_dict(self) -> Dict[str, Any]:
        return {
            "inputs": self._get_list("inputs"),
            "outputs": self._get_list("outputs"),
            "connected_to": self._get_list("connected_to")
        }

    def _logic_to_dict(self) -> Dict[str, Any]:
        return {
            "rules": self._get_list("rules", sep=";"),
            "algorithms": self._get_list("algorithms", sep=";"),
            "decision_model": self._get_list("decision_model", sep=";")
        }

    def _state_to_dict(self) -> Dict[str, Any]:
        return {
            "current": self._get_value("current", ""),
            "problems": self._get_list("problems"),
            "risks": self._get_list("risks")
        }

    def _actions_to_dict(self) -> Dict[str, Any]:
        return {
            "next_steps": self._get_list("next_steps"),
            "required_resources": self._get_list("required_resources")
        }

    def _evolution_to_dict(self) -> Dict[str, Any]:
        return {
            "history": self._get_value("history", ""),
            "future_versions": self._get_list("future_versions")
        }

    def _get_value(self, key: str, default: str = "") -> str:
        for child in self.children:
            if child.type == "Pair" and child.value == key:
                return child.children[0].value if child.children else default
        return default

    def _get_list(self, key: str, sep: str = ",") -> List[str]:
        for child in self.children:
            if child.type == "Pair" and child.value == key:
                if child.children:
                    raw = child.children[0].value
                    return [item.strip() for item in raw.split(sep) if item.strip()]
        return []


class ASTBuilder:
    """Строит семантический AST из синтаксического (CST)."""

    def build(self, cst: Dict[str, ASTNode]) -> Dict[str, SemNode]:
        """Превращает CST в семантический AST."""
        sem_ast = {}

        for rule_name, rule_node in cst.items():
            # Извлекаем все Terminal-значения из CST
            terminal_values = self._extract_terminal_values(rule_node)
            # Группируем в пары
            pairs = self._pairs_from_values(terminal_values)
            # Создаём семантический узел
            sem_node = SemNode(type=rule_name.capitalize())
            for key, val in pairs.items():
                pair_node = SemNode(type="Pair", value=key)
                val_node = SemNode(type="Value", value=val)
                pair_node.children.append(val_node)
                sem_node.children.append(pair_node)
            sem_ast[rule_name] = sem_node

        return sem_ast

    def _extract_terminal_values(self, node: ASTNode) -> List[str]:
        """Рекурсивно собирает все Terminal."""
        values = []
        if node.type == "Terminal":
            values.append(node.value)
        for child in node.children:
            values.extend(self._extract_terminal_values(child))
        return values

    def _pairs_from_values(self, values: List[str]) -> Dict[str, str]:
        """Группирует список значений в пары."""
        pairs = {}
        for i in range(0, len(values) - 1, 2):
            pairs[values[i]] = values[i + 1]
        return pairs
