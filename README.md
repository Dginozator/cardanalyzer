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

Открыть `http://127.0.0.1:8047`.

## Запуск через Docker Compose

```bash
docker compose up --build
```

Открыть `http://127.0.0.1:8047`.

Для ускорения повторных сборок включите BuildKit (используется cache pip-слоя в `Dockerfile`):

```bash
set DOCKER_BUILDKIT=1
docker compose build
```

## Prebuilt base-image (быстрый деплой без кэша)

1) Соберите базовый образ с тяжелыми зависимостями один раз:

```bash
set DOCKER_BUILDKIT=1
docker build -f Dockerfile.base -t cardanalyser-base:py311 .
```

2) Используйте его для сборки приложения без переустановки зависимостей:

```bash
set BASE_IMAGE=cardanalyser-base:py311
set INSTALL_DEPS=0
docker compose up --build
```

Для облака: запушьте `cardanalyser-base:py311` в registry и укажите полный тег в `BASE_IMAGE`.

## API форматы ответа

- `POST /api/analyze` — JSON-ответ с полями `spec` и `spec_yaml`.
- `POST /api/analyze.yaml` — чистый YAML (`Content-Type: application/x-yaml`).

## Ограничения MVP

- Извлечение `structural`/`semantic` пока заглушки (placeholder), но формат спецификации соблюдается.
- Реализованы вычисления:
  - `canvas.safe_areas` (от overlay-элементов),
  - `visual.palette.tone/saturation/temperature`,
  - `clustering_keys`.
