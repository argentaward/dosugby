# Архитектура проекта Dosug

**Dosug** — веб-приложение для сценарного подбора досуга в городах Беларуси (стартовый город — Гродно).

## 1. Общая схема

```
[Браузер (Mobile-first SPA)]
        │  REST JSON (/api/v1/*)
        ▼
[Backend: FastAPI] ──► [SQLite локально / PostgreSQL на сервере]
        ▲
        │  /admin
[Админка: sqladmin]
```

- **Единый источник правды о контрактах:** FastAPI генерирует схему OpenAPI (`/openapi.json`), из которой автоматически создаются TypeScript-типы фронтенда (`src/shared/api/schema.gen.ts`).

---

## 2. Backend (`backend/`)

### Модули по фичам (Vertical Slices)

```
backend/src/app/
├── core/                  # Инфраструктура: настройки, БД, доменные ошибки, миксины
├── modules/
│   ├── cities/            # Города
│   ├── tags/              # Группы тегов и теги (шаги квиза)
│   ├── places/            # Места, фото, жалобы на неактуальность
│   ├── scenarios/         # Готовые маршруты из нескольких мест
│   ├── recommendations/   # Скоринг и выдача рекомендаций
│   └── ingestion/         # Автосбор мест из OpenStreetMap (Overpass API) + Wikidata
├── admin/                 # Веб-админка sqladmin (/admin)
├── models_registry.py     # Реестр всех ORM-моделей для SQLAlchemy и Alembic
├── seed.py                # Начальные данные для локальной разработки
├── ingest.py              # CLI-команда синхронизации мест города с OSM/Wikidata
└── main.py                # Точка сборки FastAPI-приложения
```

### Слои внутри модуля (строго сверху вниз)

1. `router.py` — HTTP-слой: принимает запрос, вызывает сервис, возвращает Pydantic-схему.
2. `dependencies.py` — сборка зависимостей через `Depends()`.
3. `service.py` — бизнес-логика и маппинг в DTO (`schemas.py`). Кидает только доменные ошибки из `app.core.errors`.
4. `repository.py` — запросы к БД через SQLAlchemy (`AsyncSession`).
5. `models.py` — декларативные модели таблиц.

Границы слоёв автоматически проверяются утилитой **`import-linter`**.

---

## 3. Frontend (`frontend/`)

Организован по облегчённому **Feature-Sliced Design (FSD)**:

```
frontend/src/
├── app/        # Инициализация, провайдеры (QueryClient, Router), глобальные стили
├── pages/      # Страницы: home, quiz, results, place
├── widgets/    # Самостоятельные блоки интерфейса (header)
├── features/   # Действия пользователя и состояние квиза (quiz)
├── entities/   # Бизнес-сущности: city, tag, place, scenario
└── shared/     # Переиспользуемые UI-компоненты, API-клиент, платформенные утилиты
```

Правило направления импортов (`app → pages → widgets → features → entities → shared`) автоматически проверяется плагином **`eslint-plugin-boundaries`**.
