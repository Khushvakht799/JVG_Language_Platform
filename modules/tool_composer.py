"""
Модуль композиции инструментов (Tool Composer)
Для Amazon AGI Lab — тема: Tool-Use and API Orchestration
"""

from typing import Dict, List, Any, Optional
import json
import yaml

class ToolComposer:
    """Композитор инструментов для агентов."""
    
    def __init__(self, tool_registry: Dict[str, Dict[str, Any]]):
        self.tool_registry = tool_registry
        
    def compose_tool_chain(self, task: str) -> List[Dict[str, Any]]:
        """Составляет цепочку инструментов для выполнения задачи."""
        # Простейшая эвристика: выбираем инструменты по ключевым словам.
        keywords = task.lower().split()
        selected_tools = []
        for tool_name, tool_info in self.tool_registry.items():
            if any(kw in tool_info.get("keywords", []) for kw in keywords):
                selected_tools.append(tool_info)
        return selected_tools
    
    def generate_tool_config(self, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Генерирует конфигурацию для Amazon Bedrock Agents."""
        config = {
            "api_schema": {
                "openapi": "3.0.0",
                "paths": {}
            }
        }
        for tool in tools:
            path = f"/{tool.get('name', 'default')}"
            config["api_schema"]["paths"][path] = {
                "post": {
                    "summary": tool.get("description", ""),
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": tool.get("input_schema", {})
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": tool.get("output_schema", {})
                                }
                            }
                        }
                    }
                }
            }
        return config

def load_tool_registry_from_file(file_path: str) -> Dict[str, Dict[str, Any]]:
    """Загружает реестр инструментов из JSON-файла."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("tools", {})


def generate_tool_composer_config(output_path: str = "configs/tool_composer.json"):
    config = {
        "name": "ToolComposer",
        "version": "1.0",
        "description": "Модуль композиции инструментов для AGI Lab",
        "tools": [
            {
                "name": "calculator",
                "description": "Выполняет математические операции",
                "keywords": ["calculate", "math", "sum", "multiply"],
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"}
                    }
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "result": {"type": "number"}
                    }
                }
            },
            {
                "name": "weather",
                "description": "Получает данные о погоде",
                "keywords": ["weather", "temperature", "forecast"],
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "date": {"type": "string"}
                    }
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "temperature": {"type": "number"},
                        "condition": {"type": "string"}
                    }
                }
            }
        ]
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return config


if __name__ == "__main__":
    # Реестр инструментов (в реальности загружается из файла)
    tool_registry = {
        "calculator": {
            "name": "calculator",
            "description": "Выполняет математические операции",
            "keywords": ["calculate", "math", "sum", "multiply"]
        },
        "weather": {
            "name": "weather",
            "description": "Получает данные о погоде",
            "keywords": ["weather", "temperature", "forecast"]
        }
    }
    composer = ToolComposer(tool_registry)
    task = "Calculate the total cost and check weather in Barcelona"
    chain = composer.compose_tool_chain(task)
    print("Цепочка инструментов:", json.dumps(chain, indent=2, ensure_ascii=False))
    config = generate_tool_composer_config()
    print("Конфигурация сохранена.")
