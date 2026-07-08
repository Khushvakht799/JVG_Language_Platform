# JVG Language Platform

## Описание
JVG (JSON Vectorograph) — платформа для описания, хранения, поиска и исполнения сущностей, процессов, систем и связей.

## Быстрый старт

### Установка
```bash
git clone <repo>
cd JVG_Language_Platform
pip install -r requirements.txt
Запуск API
bash
python api.py
API будет доступен по адресу: http://localhost:8000

Использование
Компиляция текста в JVG
bash
curl -X POST http://localhost:8000/compile -H "Content-Type: application/json" -d '{"text":"entity:\n  name: Моя система\n  type: система\n  purpose: тест"}'
Поиск по запросу
bash
curl -X POST http://localhost:8000/search -H "Content-Type: application/json" -d '{"query":"система","top_k":5}'
Инструменты
bash
python tools.py doctor   # диагностика
python tools.py graph    # визуализация графа
python tools.py rebuild  # пересборка индексов
Архитектура
01_toolchain/ — компилятор, валидатор, хранилище

02_search/ — векторизация, ранжирование

03_runtime/ — среда исполнения

Лицензия
MIT
