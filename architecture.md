# ARCHITECTURE.md

## Назначение документа

Данный документ фиксирует архитектурные решения проекта **внутреннего корпоративного сервиса управления бизнес‑требованиями**.

Документ является **архитектурным контрактом** между архитектором/PM и любыми исполнителями (включая Codex).

Любые отклонения от описанных принципов допускаются **только после явного согласования**.

---

## 1. Общая архитектурная схема

```
HTTP (FastAPI + Jinja2)
        ↓
Application Services (use-cases, транзакции)
        ↓
Domain (бизнес‑правила, статусы)
        ↓
Repositories (SQLAlchemy)
        ↓
Database (SQLite → Postgres)
```

### Ключевые принципы

- HTTP‑слой не содержит бизнес‑логики
- Все сценарии выполняются через application‑services
- Статусы и правила находятся в domain
- Репозитории работают только с БД
- Транзакциями управляет application‑layer

---

## 2. Технологический стек (утверждён)

- Python + FastAPI
- Server‑side HTML (Jinja2) + минимальный JS
- Один backend‑сервис
- SQLite (MVP) → Postgres (без смены архитектуры)
- SQLAlchemy + Alembic
- Docker + GitLab CI
- Без frontend‑фреймворков

---

## 3. Слои приложения

### Presentation

- FastAPI роуты
- HTML‑шаблоны (Jinja2)
- Валидация входных данных

### Application

- Use‑cases (сценарии)
- Управление транзакциями
- Оркестрация между доменом и репозиториями

### Domain

- Бизнес‑правила
- Статусы документов и согласований
- Инварианты

### Infrastructure

- SQLAlchemy модели
- Репозитории
- Сессии БД
- Alembic миграции

---

## 4. Backend‑модули и сервисы

### Users

**Service:** UserService

- register\_user
- authenticate\_user
- get\_profile
- update\_user
- deactivate\_user

### Documents

**Service:** DocumentService

- create\_draft
- update\_draft
- submit\_for\_approval
- return\_for\_revision
- reject\_document
- archive\_document
- get\_document
- list\_documents

### Approvals

**Service:** ApprovalService

- create\_approval\_flow
- approve\_step
- reject\_step
- recalc\_approval\_status

ApprovalStep не имеет отдельного сервиса и управляется через ApprovalService.

### Comments

**Service:** CommentService

- add\_comment
- list\_comments\_for\_document
- list\_comments\_for\_approval

### DocumentMetric

**Service:** DocumentMetricService

- add\_metric
- update\_metric
- delete\_metric
- list\_metrics

### DocumentRICE

**Service:** DocumentRICEService

- upsert\_rice
- get\_rice
- recalc\_score

---

## 5. Dependency Injection

Единая точка DI: `di/providers.py`

Поставляет:

- DB session
- Репозитории
- Application‑services

---

## 6. HTML и UI

- Server‑side rendering (Jinja2)
- Минимальный JS (динамические поля, вкладки RICE, комментарии)
- Интерфейс полностью на русском языке

---

```
```

