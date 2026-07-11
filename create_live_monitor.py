from jvg import JVGStore

store = JVGStore()

doc = {
    "vectorograph": {
        "meta": {"title": "Живой монитор"},
        "entity": {"name": "Монитор", "type": "процесс"},
        "state": {"current": "ПРОВЕРКА"},
        "state_machine": {
            "initial": "ПРОВЕРКА",
            "states": ["ПРОВЕРКА", "РАБОТАЕТ", "НЕ_РАБОТАЕТ", "ПЕРЕЗАПУСК", "ОЖИДАНИЕ"],
            "transitions": [
                {"from": "ПРОВЕРКА", "to": "РАБОТАЕТ"},
                {"from": "ПРОВЕРКА", "to": "НЕ_РАБОТАЕТ"},
                {"from": "РАБОТАЕТ", "to": "ОЖИДАНИЕ"},
                {"from": "НЕ_РАБОТАЕТ", "to": "ПЕРЕЗАПУСК"},
                {"from": "ПЕРЕЗАПУСК", "to": "ОЖИДАНИЕ"},
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
                    "condition": "state == ПЕРЕЗАПУСК",
                    "action": "run_powershell",
                    "action_params": {"command": "Write-Host 'Перезапуск сервера...'"}
                },
                {
                    "condition": "state == ОЖИДАНИЕ",
                    "action": "run_powershell",
                    "action_params": {"command": "Write-Host 'Ожидание перед следующей проверкой...'"}
                }
            ]
        }
    }
}

doc_id = store.create(doc)
print(f"✅ Живой монитор создан: {doc_id}")
