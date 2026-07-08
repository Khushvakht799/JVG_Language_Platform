"""
compiler.py — Компилятор JVG (документный)
Принимает текст в упрощённом формате и превращает в JVG JSON.
"""

import json
import re
from typing import Dict, Any, List

class JVGCompiler:
    def __init__(self):
        self.sections = [
            "meta", "entity", "context", "structure", 
            "relations", "logic", "state", "actions", "evolution"
        ]

    def compile(self, text: str) -> Dict[str, Any]:
        """
        Принимает текст вида:
        
        meta:
          version: 1.0
          title: Тестовый JVG
          date: 2026-07-07
          author: Архитектор
          status: черновик
        
        entity:
          name: Сервер
          type: система
          purpose: обработка данных
        """
        result = {
            "vectorograph": {
                "meta": {"version": "1.0", "title": "", "date": "", "author": "", "status": ""},
                "entity": {"name": "", "type": "", "purpose": ""},
                "context": {"origin": "", "environment": "", "dependencies": []},
                "structure": {"components": [], "layers": []},
                "relations": {"inputs": [], "outputs": [], "connected_to": []},
                "logic": {"rules": [], "algorithms": [], "decision_model": []},
                "state": {"current": "", "problems": [], "risks": []},
                "actions": {"next_steps": [], "required_resources": []},
                "evolution": {"history": "", "future_versions": []}
            }
        }

        # Разбиваем текст на секции
        current_section = None
        current_data = {}
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Проверяем, не начинается ли новая секция
            section_match = re.match(r'^([a-zA-Z_]+):\s*$', line)
            if section_match:
                # Сохраняем предыдущую секцию
                if current_section and current_data:
                    self._fill_section(result, current_section, current_data)
                current_section = section_match.group(1)
                current_data = {}
                continue

            # Если мы внутри секции, парсим ключ: значение
            if current_section:
                kv_match = re.match(r'^\s*([a-zA-Z_]+)\s*:\s*(.*)$', line)
                if kv_match:
                    key = kv_match.group(1)
                    val = kv_match.group(2).strip()
                    # Убираем кавычки, если есть
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    current_data[key] = val

        # Сохраняем последнюю секцию
        if current_section and current_data:
            self._fill_section(result, current_section, current_data)

        return {"status": "success", "jvg": result}

    def _fill_section(self, result: Dict, section: str, data: Dict):
        target = result["vectorograph"].get(section)
        if not target:
            return

        for key, value in data.items():
            if key in target:
                if isinstance(target[key], list):
                    # Разбиваем строку по запятой или точке с запятой
                    if ";" in value:
                        items = [item.strip() for item in value.split(";") if item.strip()]
                    else:
                        items = [item.strip() for item in value.split(",") if item.strip()]
                    target[key] = items
                else:
                    target[key] = value


# ============================================================
# Тест
# ============================================================

def test_compiler():
    sample = """
meta:
  version: 1.0
  title: Тестовый JVG
  date: 2026-07-07
  author: Архитектор
  status: черновик

entity:
  name: Сервер
  type: система
  purpose: обработка данных

context:
  origin: тестовый проект
  environment: локальная сеть
  dependencies: БД, API

structure:
  components: ядро, модули, интерфейс
  layers: приложение, сервис, хранилище

relations:
  inputs: запросы REST
  outputs: ответы JSON
  connected_to: база данных, кэш

logic:
  rules: обработка ошибок; валидация
  algorithms: поиск; сортировка
  decision_model: приоритет по времени

state:
  current: ВЫПОЛНЕНИЕ
  problems: нет
  risks: низкий

actions:
  next_steps: протестировать, развернуть
  required_resources: сервер, доступы

evolution:
  history: начало проекта
  future_versions: v2.0, v3.0
"""

    compiler = JVGCompiler()
    result = compiler.compile(sample)
    
    if result["status"] == "success":
        print("✅ Компиляция успешна!")
        print("\n=== JVG ===")
        print(json.dumps(result["jvg"], indent=2, ensure_ascii=False))
    else:
        print("❌ Ошибка:", result.get("errors"))

if __name__ == "__main__":
    test_compiler()
