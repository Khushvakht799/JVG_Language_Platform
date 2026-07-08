"""
validator.py — Валидатор JVG
Проверяет, что JVG-документ соответствует схеме.
"""

from typing import Dict, Any, List, Tuple

class JVGValidator:
    def __init__(self):
        # Определяем схему
        self.schema = {
            "meta": {
                "required": ["version", "title", "date", "author", "status"],
                "types": {
                    "version": str,
                    "title": str,
                    "date": str,
                    "author": str,
                    "status": str
                },
                "allowed_values": {
                    "status": ["черновик", "готово", "уточняется"]
                }
            },
            "entity": {
                "required": ["name", "type", "purpose"],
                "types": {
                    "name": str,
                    "type": str,
                    "purpose": str
                },
                "allowed_values": {
                    "type": ["система", "процесс", "идея", "агент"]
                }
            },
            "context": {
                "required": ["origin", "environment", "dependencies"],
                "types": {
                    "origin": str,
                    "environment": str,
                    "dependencies": list
                }
            },
            "structure": {
                "required": ["components", "layers"],
                "types": {
                    "components": list,
                    "layers": list
                }
            },
            "relations": {
                "required": ["inputs", "outputs", "connected_to"],
                "types": {
                    "inputs": list,
                    "outputs": list,
                    "connected_to": list
                }
            },
            "logic": {
                "required": ["rules", "algorithms", "decision_model"],
                "types": {
                    "rules": list,
                    "algorithms": list,
                    "decision_model": list
                }
            },
            "state": {
                "required": ["current", "problems", "risks"],
                "types": {
                    "current": str,
                    "problems": list,
                    "risks": list
                },
                "allowed_values": {
                    "current": ["ИССЛЕДОВАНИЕ", "ПРОЕКТИРОВАНИЕ", "ВЫПОЛНЕНИЕ", "ЗАБЛОКИРОВАНО", "ЗАВЕРШЕНО", "ОТЛОЖЕНО"]
                }
            },
            "actions": {
                "required": ["next_steps", "required_resources"],
                "types": {
                    "next_steps": list,
                    "required_resources": list
                }
            },
            "evolution": {
                "required": ["history", "future_versions"],
                "types": {
                    "history": str,
                    "future_versions": list
                }
            }
        }

    def validate(self, jvg: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Проверяет JVG-документ.
        Возвращает (валидность, список ошибок).
        """
        errors = []

        # Проверяем, что есть корневой ключ
        if "vectorograph" not in jvg:
            errors.append("Отсутствует корневой ключ 'vectorograph'")
            return False, errors

        data = jvg["vectorograph"]

        # Проверяем каждую секцию
        for section_name, section_schema in self.schema.items():
            if section_name not in data:
                errors.append(f"Отсутствует секция '{section_name}'")
                continue

            section = data[section_name]
            self._validate_section(section_name, section, section_schema, errors)

        return len(errors) == 0, errors

    def _validate_section(self, section_name: str, section: Dict, schema: Dict, errors: List[str]):
        """Проверяет одну секцию."""
        # Проверяем обязательные поля
        for required_field in schema.get("required", []):
            if required_field not in section:
                errors.append(f"В секции '{section_name}' отсутствует обязательное поле '{required_field}'")

        # Проверяем типы
        for field_name, expected_type in schema.get("types", {}).items():
            if field_name in section:
                value = section[field_name]
                if not isinstance(value, expected_type):
                    errors.append(
                        f"Поле '{section_name}.{field_name}' должно быть типа {expected_type.__name__}, "
                        f"получено {type(value).__name__}"
                    )

        # Проверяем допустимые значения
        for field_name, allowed_values in schema.get("allowed_values", {}).items():
            if field_name in section:
                value = section[field_name]
                if value not in allowed_values:
                    errors.append(
                        f"Поле '{section_name}.{field_name}' должно быть одним из {allowed_values}, "
                        f"получено '{value}'"
                    )


# ============================================================
# Тест
# ============================================================

def test_validator():
    # Пример JVG
    jvg = {
        "vectorograph": {
            "meta": {
                "version": "1.0",
                "title": "Тестовый JVG",
                "date": "2026-07-07",
                "author": "Архитектор",
                "status": "черновик"
            },
            "entity": {
                "name": "Сервер",
                "type": "система",
                "purpose": "обработка данных"
            },
            "context": {
                "origin": "тестовый проект",
                "environment": "локальная сеть",
                "dependencies": ["БД", "API"]
            },
            "structure": {
                "components": ["ядро", "модули"],
                "layers": ["приложение", "сервис"]
            },
            "relations": {
                "inputs": ["запросы REST"],
                "outputs": ["ответы JSON"],
                "connected_to": ["база данных"]
            },
            "logic": {
                "rules": ["обработка ошибок"],
                "algorithms": ["поиск"],
                "decision_model": ["приоритет по времени"]
            },
            "state": {
                "current": "ВЫПОЛНЕНИЕ",
                "problems": ["нет"],
                "risks": ["низкий"]
            },
            "actions": {
                "next_steps": ["протестировать"],
                "required_resources": ["сервер"]
            },
            "evolution": {
                "history": "начало проекта",
                "future_versions": ["v2.0"]
            }
        }
    }

    validator = JVGValidator()
    valid, errors = validator.validate(jvg)

    if valid:
        print("✅ JVG валиден")
    else:
        print("❌ Ошибки валидации:")
        for err in errors:
            print(f"  {err}")

if __name__ == "__main__":
    test_validator()
