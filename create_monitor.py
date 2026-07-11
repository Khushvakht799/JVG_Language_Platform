from jvg import JVGStore

store = JVGStore()

doc = {
    "vectorograph": {
        "meta": {"title": "Мониторинг сервера"},
        "entity": {"name": "Монитор", "type": "процесс"},
        "state": {"current": "ПРОВЕРКА"},
        "state_machine": {
            "initial": "ПРОВЕРКА",
            "states": ["ПРОВЕРКА", "РАБОТАЕТ", "НЕ_РАБОТАЕТ"],
            "transitions": [
                {"from": "ПРОВЕРКА", "to": "РАБОТАЕТ"},
                {"from": "ПРОВЕРКА", "to": "НЕ_РАБОТАЕТ"}
            ],
            "rules": [
                {
                    "condition": "state == ПРОВЕРКА",
                    "action": "http_request",
                    "action_params": {
                        "url": "https://httpbin.org/get"
                    }
                }
            ]
        }
    }
}

doc_id = store.create(doc)
print(f"✅ Документ создан: {doc_id}")
