# JVG Language Platform v2.0

**JVG (JSON Vectorograph)** — это исполняемая семантическая платформа, которая превращает описание процессов в реальные действия.  
Она позволяет хранить знания как структурированные графы (JVG-документы), управлять ими через конечные автоматы (FSM) и исполнять действия через подключаемые исполнители (Executors).

## 🧠 Основные возможности

| Возможность | Описание |
| :--- | :--- |
| **Хранилище знаний** | Хранение JVG-документов с версионированием и логическими именами (`create`, `update`, `find`). |
| **Семантический поиск** | Поиск по смыслу, структуре и состоянию (через `ranking` и `vectorizer`). |
| **Конечный автомат (FSM)** | Логика переходов и правил хранится **внутри JVG-документа**, а не в коде. |
| **Исполнение действий (Action Executor)** | Выполнение команд через `run_cmd`, `run_powershell`, `open_url` и другие исполнители. |
| **Логирование и аудит** | Каждое действие логируется, есть поддержка `rollback`. |
| **Расширяемость** | Можно подключать новые исполнители через `ExecutorRegistry` без изменения ядра. |
| **CLI и API** | Управление через командную строку (`jvg.cli`) и REST API (FastAPI). |
| **Визуализация** | Построение графов связей между документами (GraphViz). |
| **Интеграция с Cognitive OS** | Готовые адаптеры для L1–L5 (события, память, модели, исполнение, аудит). |

---

## 🚀 5 сценариев использования (с работающими командами)

### 1. Создать и сохранить JVG-документ
```powershell
python -c "from jvg import JVGStore; s=JVGStore(); doc_id=s.create({'vectorograph':{'entity':{'name':'Моя система','type':'система'},'state':{'current':'ИССЛЕДОВАНИЕ'}}}); print(doc_id)"
2. Поиск документа по логическому имени
powershell
python -c "from jvg import JVGStore; print(JVGStore().find('Моя система'))"
3. Обновить состояние документа через Runtime (FSM)
powershell
python -m jvg.cli.tools run Перезапуск_Explorer --debug
4. Выполнить PowerShell-команду через Action Executor
powershell
python -c "from jvg import ActionExecutor; print(ActionExecutor.execute('run_powershell', {'command':'Write-Host \"Привет от JVG!\"'}).stdout)"
5. Открыть URL (демонстрация работы Executor)
powershell
python -c "from jvg import ActionExecutor; ActionExecutor.execute('open_url', {'url':'https://example.com'}); print('URL открыт')"
📁 Структура проекта
text
jvg/
├── core/           # Конфигурация
├── storage/        # Хранилище (create, update, find, delete)
├── runtime/        # Runtime + FSM Engine
├── execution/      # Action Executor, Registry, Executors
├── fsm/            # Конечный автомат
├── cli/            # Команды: list, run, doctor, fsm
├── compiler/       # Компилятор
├── validator/      # Валидатор
├── search/         # Векторизация и ранжирование
├── identity/       # UID и версионирование
└── adapters/       # Интеграция с внешними системами (планируется)
🔧 Быстрый старт
powershell
# Клонировать репозиторий
git clone https://github.com/Khushvakht799/JVG_Language_Platform.git
cd JVG_Language_Platform

# Установить зависимости
pip install -r requirements.txt

# Проверить систему
python -m jvg.cli.doctor

# Посмотреть документы
python -m jvg.cli.tools list
📜 Лицензия
MIT
