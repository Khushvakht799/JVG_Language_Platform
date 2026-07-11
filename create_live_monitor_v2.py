from jvg import JVGStore

store = JVGStore()

doc = {
    "vectorograph": {
        "meta": {"title": "Живой монитор v2"},
        "entity": {"name": "Монитор v2", "type": "процесс"},
        "state": {"current": "ПРОВЕРКА"},
        "state_machine": {
            "initial": "ПРОВЕРКА",
            "states": ["ПРОВЕРКА", "РАБОТАЕТ", "НЕ_РАБОТАЕТ", "ОЖИДАНИЕ"],
            "transitions": [
                {"from": "ПРОВЕРКА", "to": "РАБОТАЕТ"},
                {"from": "ПРОВЕРКА", "to": "НЕ_РАБОТАЕТ"},
                {"from": "РАБОТАЕТ", "to": "ОЖИДАНИЕ"},
                {"from": "НЕ_РАБОТАЕТ", "to": "ОЖИДАНИЕ"},
                {"from": "ОЖИДАНИЕ", "to": "ПРОВЕРКА"}
            ],
            "rules": [
                {
                    "condition": "state == ПРОВЕРКА",
                    "action": "http_request",
                    "action_params": {"url": "https://httpbin.org/get"}
                },
                {
                    "condition": "state == РАБОТАЕТ",
                    "action": "run_powershell",
                    "action_params": {"command": "Write-Host 'Сервер работает'"}
                },
                {
                    "condition": "state == НЕ_РАБОТАЕТ",
                    "action": "run_powershell",
                    "action_params": {"command": "Write-Host 'Сервер не отвечает'"}
                },
                {
                    "condition": "state == ОЖИДАНИЕ",
                    "action": "run_powershell",
                    "action_params": {"command": "Write-Host 'Ожидание...'"}
                }
            ],
            "fact_rules": [
                {
                    "condition": "fact.http.status_code == 200",
                    "to": "РАБОТАЕТ"
                },
                {
                    "condition": "fact.http.status_code != 200",
                    "to": "НЕ_РАБОТАЕТ"
                }
            ]
        }
    }
}

doc_id = store.create(doc)
print(f"✅ Живой монитор v2 создан: {doc_id}")
