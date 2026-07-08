"""
library.py — Стандартная библиотека JVG
Готовые шаблоны для типовых сущностей.
"""

from typing import Dict, Any, Optional
from datetime import datetime

class JVGLibrary:
    """Библиотека шаблонов JVG."""
    
    @staticmethod
    def system_template(name: str, purpose: str, origin: str = "стандартный шаблон") -> Dict[str, Any]:
        """Шаблон для систем."""
        return {
            "vectorograph": {
                "meta": {
                    "version": "1.0",
                    "title": name,
                    "date": datetime.now().isoformat(),
                    "author": "Стандартная библиотека",
                    "status": "черновик"
                },
                "entity": {
                    "name": name,
                    "type": "система",
                    "purpose": purpose
                },
                "context": {
                    "origin": origin,
                    "environment": "не указано",
                    "dependencies": []
                },
                "structure": {
                    "components": ["ядро", "модули", "интерфейс"],
                    "layers": ["приложение", "сервис", "хранилище"]
                },
                "relations": {
                    "inputs": ["входные данные"],
                    "outputs": ["выходные данные"],
                    "connected_to": ["внешние системы"]
                },
                "logic": {
                    "rules": ["правило 1", "правило 2"],
                    "algorithms": ["алгоритм 1", "алгоритм 2"],
                    "decision_model": ["модель принятия решений"]
                },
                "state": {
                    "current": "ИССЛЕДОВАНИЕ",
                    "problems": [],
                    "risks": ["стандартные риски"]
                },
                "actions": {
                    "next_steps": ["проанализировать", "спроектировать", "реализовать"],
                    "required_resources": ["люди", "время", "инфраструктура"]
                },
                "evolution": {
                    "history": "создано из шаблона",
                    "future_versions": ["v1.0", "v2.0"]
                }
            }
        }
    
    @staticmethod
    def process_template(name: str, purpose: str, origin: str = "стандартный шаблон") -> Dict[str, Any]:
        """Шаблон для процессов."""
        return {
            "vectorograph": {
                "meta": {
                    "version": "1.0",
                    "title": name,
                    "date": datetime.now().isoformat(),
                    "author": "Стандартная библиотека",
                    "status": "черновик"
                },
                "entity": {
                    "name": name,
                    "type": "процесс",
                    "purpose": purpose
                },
                "context": {
                    "origin": origin,
                    "environment": "не указано",
                    "dependencies": ["участники", "ресурсы"]
                },
                "structure": {
                    "components": ["этап 1", "этап 2", "этап 3"],
                    "layers": ["планирование", "выполнение", "контроль"]
                },
                "relations": {
                    "inputs": ["входные условия"],
                    "outputs": ["результат"],
                    "connected_to": ["смежные процессы"]
                },
                "logic": {
                    "rules": ["условие запуска", "условие завершения"],
                    "algorithms": ["шаг 1", "шаг 2", "шаг 3"],
                    "decision_model": ["проверка качества"]
                },
                "state": {
                    "current": "ИССЛЕДОВАНИЕ",
                    "problems": [],
                    "risks": ["задержки", "нехватка ресурсов"]
                },
                "actions": {
                    "next_steps": ["проверить готовность", "запустить", "отслеживать"],
                    "required_resources": ["документация", "инструменты"]
                },
                "evolution": {
                    "history": "создано из шаблона",
                    "future_versions": ["v1.0", "v2.0"]
                }
            }
        }
    
    @staticmethod
    def agent_template(name: str, purpose: str, origin: str = "стандартный шаблон") -> Dict[str, Any]:
        """Шаблон для агентов."""
        return {
            "vectorograph": {
                "meta": {
                    "version": "1.0",
                    "title": name,
                    "date": datetime.now().isoformat(),
                    "author": "Стандартная библиотека",
                    "status": "черновик"
                },
                "entity": {
                    "name": name,
                    "type": "агент",
                    "purpose": purpose
                },
                "context": {
                    "origin": origin,
                    "environment": "не указано",
                    "dependencies": ["база знаний", "инструменты"]
                },
                "structure": {
                    "components": ["восприятие", "мышление", "действие"],
                    "layers": ["сенсорный", "когнитивный", "моторный"]
                },
                "relations": {
                    "inputs": ["стимулы", "запросы"],
                    "outputs": ["ответы", "действия"],
                    "connected_to": ["пользователи", "системы"]
                },
                "logic": {
                    "rules": ["правило обработки", "правило вывода"],
                    "algorithms": ["анализ", "принятие решения"],
                    "decision_model": ["модель агента"]
                },
                "state": {
                    "current": "ИССЛЕДОВАНИЕ",
                    "problems": [],
                    "risks": ["некорректные данные", "сбой инструментов"]
                },
                "actions": {
                    "next_steps": ["проанализировать контекст", "определить цель", "выполнить"],
                    "required_resources": ["модель", "данные", "инструменты"]
                },
                "evolution": {
                    "history": "создано из шаблона",
                    "future_versions": ["v1.0", "v2.0"]
                }
            }
        }
    
    @staticmethod
    def idea_template(name: str, purpose: str, origin: str = "стандартный шаблон") -> Dict[str, Any]:
        """Шаблон для идей."""
        return {
            "vectorograph": {
                "meta": {
                    "version": "1.0",
                    "title": name,
                    "date": datetime.now().isoformat(),
                    "author": "Стандартная библиотека",
                    "status": "черновик"
                },
                "entity": {
                    "name": name,
                    "type": "идея",
                    "purpose": purpose
                },
                "context": {
                    "origin": origin,
                    "environment": "не указано",
                    "dependencies": ["вдохновение", "контекст"]
                },
                "structure": {
                    "components": ["суть", "обоснование", "реализация"],
                    "layers": ["концептуальный", "логический", "практический"]
                },
                "relations": {
                    "inputs": ["проблема", "возможность"],
                    "outputs": ["решение", "проект"],
                    "connected_to": ["смежные идеи"]
                },
                "logic": {
                    "rules": ["логика идеи"],
                    "algorithms": ["развитие идеи"],
                    "decision_model": ["оценка идеи"]
                },
                "state": {
                    "current": "ИССЛЕДОВАНИЕ",
                    "problems": [],
                    "risks": ["нереализуемость"]
                },
                "actions": {
                    "next_steps": ["проверить", "разработать", "представить"],
                    "required_resources": ["время", "экспертиза"]
                },
                "evolution": {
                    "history": "создано из шаблона",
                    "future_versions": ["v1.0"]
                }
            }
        }


def get_template(template_type: str, name: str, purpose: str, origin: str = "стандартный шаблон") -> Dict[str, Any]:
    """Универсальная функция для получения шаблона."""
    library = JVGLibrary()
    templates = {
        "система": library.system_template,
        "процесс": library.process_template,
        "агент": library.agent_template,
        "идея": library.idea_template
    }
    if template_type not in templates:
        raise ValueError(f"Неизвестный тип шаблона: {template_type}. Доступны: {list(templates.keys())}")
    return templates[template_type](name, purpose, origin)


# ============================================================
# Тест
# ============================================================

def test_library():
    print("=== Стандартная библиотека JVG ===")
    
    library = JVGLibrary()
    
    # Создаём системный шаблон
    system = library.system_template("Тестовая система", "тестирование библиотеки")
    print(f"✅ Система: {system['vectorograph']['entity']['name']} ({system['vectorograph']['entity']['type']})")
    
    # Создаём шаблон агента
    agent = library.agent_template("Тестовый агент", "помощь в тестировании")
    print(f"✅ Агент: {agent['vectorograph']['entity']['name']} ({agent['vectorograph']['entity']['type']})")
    
    # Универсальная функция
    process = get_template("процесс", "Тестовый процесс", "отработка шаблонов")
    print(f"✅ Процесс: {process['vectorograph']['entity']['name']} ({process['vectorograph']['entity']['type']})")


if __name__ == "__main__":
    test_library()
