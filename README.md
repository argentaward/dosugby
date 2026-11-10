# Dosug — веб-приложение подбора досуга

Веб-приложение, которое помогает выбрать, куда сходить в свободное время (начиная с Гродно и далее по всей Беларуси) на основе короткого квиза: **С кем → Какой вайб → Погода и бюджет**.

## Документация

- [Архитектура проекта](docs/ARCHITECTURE.md)
- [Правила разработки и качества кода](docs/CODE_RULES.md)
- Архитектурные решения (ADR): [0001 — Стек](docs/adr/0001-stack.md), [0002 — Модель тегов](docs/adr/0002-tags-model.md)

---

## Быстрый старт (локально)

### 1. Запуск Backend (FastAPI + SQLite)

```powershell
cd backend
Copy-Item .env.example .env
python -m uv sync
python -m uv run alembic upgrade head
python -m uv run python -m app.seed
# Автоматический сбор реальных мест Гродно из OpenStreetMap + Wikidata:
python -m uv run python -m app.ingest --city grodno --radius 10000
python -m uv run uvicorn app.main:app --reload --port 8000
```

После запуска доступны:
- **Swagger UI (API):** `http://localhost:8000/docs`
- **Админ-панель (`sqladmin`):** `http://localhost:8000/admin` (логин/пароль из `backend/.env`, по умолчанию `admin` / `change-me`)

### 2. Запуск Frontend (React + Vite)

В новом окне терминала:

```powershell
cd frontend
npm install
npm run dev
```

Откройте `http://localhost:5173`.

---

## Проверка качества кода

### Backend
```powershell
cd backend
python -m uv run ruff format --check .
python -m uv run ruff check .
python -m uv run mypy
python -m uv run lint-imports
python -m uv run pytest --cov
```

### Frontend
```powershell
cd frontend
npm run check
npm run build
```

### Обновление TypeScript-типов после изменений в API бэкенда
При запущенном бэкенде на порту `8000`:
```powershell
cd frontend
npm run api:gen
```
