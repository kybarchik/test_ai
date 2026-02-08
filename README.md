# MVP FastAPI Service

## Запуск через Docker

```bash
docker build -t mvp-app .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname \
  -e SECRET_KEY=change-me \
  -e ENVIRONMENT=production \
  mvp-app
```

## Миграции

```bash
alembic upgrade head
```

## Создание первого пользователя

```bash
python -m app.cli create-user --username admin --password secret
```
