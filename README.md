# Card Analyser MVP

Web-приложение для базового сценария:
1. Открыть главную страницу.
2. Вставить карточку товара через Ctrl+V.
3. Отправить на обработку.
4. Нормализовать картинку к 3:4 и 900x1200.
5. Вернуть JSON в формате `spec-template.md`.

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Открыть `http://127.0.0.1:8000`.

## Ограничения MVP

- Извлечение `structural`/`semantic` пока заглушки (placeholder), но формат спецификации соблюдается.
- Реализованы вычисления:
  - `canvas.safe_areas` (от overlay-элементов),
  - `visual.palette.tone/saturation/temperature`,
  - `clustering_keys`.
