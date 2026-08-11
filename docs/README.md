# JVG Platform API Documentation

## Swagger UI

Доступен по адресу: `http://localhost:8000/docs`

## OpenAPI Schema

Файл: `openapi.json`

## Эндпоинты

- `GET /` — корневой путь
- `GET /health` — проверка состояния
- `POST /step` — выполнить шаг для JVG-документа
- `GET /doc/{doc_id}` — получить документ по ID

## Пример запроса

```bash
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"doc_id":"test_doc","new_state":"ВЫПОЛНЕНИЕ"}'
Версия
0.1.0
