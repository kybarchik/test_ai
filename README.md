# MVP FastAPI Service

## Локальный запуск

1. Установите зависимости:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install aiosqlite
```

2. Задайте переменные окружения:

```bash
export DATABASE_URL="sqlite+aiosqlite:///./data/app.db"
export SECRET_KEY="change-me"
export ENVIRONMENT="development"
```

3. Примените миграции и запустите приложение:

```bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Запуск через Docker

### docker run

```bash
docker build -t mvp-app .
docker run -p 8000:8000 \
  -e DATABASE_URL="sqlite+aiosqlite:///./data/app.db" \
  -e SECRET_KEY=change-me \
  -e ENVIRONMENT=production \
  -v $(pwd)/data:/app/data \
  mvp-app
```

### docker compose

```bash
docker compose up --build
```

## Переменные окружения

| Переменная | Назначение | Пример |
| --- | --- | --- |
| `DATABASE_URL` | Строка подключения к БД | `sqlite+aiosqlite:///./data/app.db` |
| `SECRET_KEY` | Секрет для JWT/сессий | `change-me` |
| `ENVIRONMENT` | Окружение приложения | `development` |

## Переход на Postgres

Для перехода на Postgres замените `DATABASE_URL`, например:

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/dbname"
```
