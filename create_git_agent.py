"""
create_git_agent.py — Git-агент для автоматических коммитов и пуша
"""

from jvg import JVGStore

store = JVGStore()

doc = {
    "vectorograph": {
        "meta": {"title": "Git Автоматизация", "author": "JVG"},
        "entity": {"name": "GitAgent", "type": "агент"},
        "state": {"current": "ОЖИДАНИЕ"},
        "state_machine": {
            "initial": "ОЖИДАНИЕ",
            "states": ["ОЖИДАНИЕ", "ДИАГНОСТИКА", "ДОБАВЛЕНИЕ", "КОММИТ", "ПУШ", "ЗАВЕРШЕНО"],
            "transitions": [
                {"from": "ОЖИДАНИЕ", "to": "ДИАГНОСТИКА"},
                {"from": "ДИАГНОСТИКА", "to": "ДОБАВЛЕНИЕ"},
                {"from": "ДОБАВЛЕНИЕ", "to": "КОММИТ"},
                {"from": "КОММИТ", "to": "ПУШ"},
                {"from": "ПУШ", "to": "ЗАВЕРШЕНО"}
            ],
            "rules": [
                {
                    "condition": "state == ДИАГНОСТИКА",
                    "action": "run_git",
                    "action_params": {"command": "status", "repo_path": "."}
                },
                {
                    "condition": "state == ДОБАВЛЕНИЕ",
                    "action": "run_git",
                    "action_params": {"command": "add .", "repo_path": "."}
                },
                {
                    "condition": "state == КОММИТ",
                    "action": "run_git",
                    "action_params": {"command": "commit -m \"JVG automatic commit\"", "repo_path": "."}
                },
                {
                    "condition": "state == ПУШ",
                    "action": "run_git",
                    "action_params": {"command": "push", "repo_path": "."}
                }
            ]
        }
    }
}

doc_id = store.create(doc)
print(f"✅ Git-агент создан: {doc_id}")
