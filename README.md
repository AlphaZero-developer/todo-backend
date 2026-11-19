# Todo App Backend

REST API для списка задач: **FastAPI + PostgreSQL + Redis**, всё запускается в Docker Compose одной командой.
Список задач кэшируется в Redis и сбрасывается при любом изменении.

## Быстрый старт

Нужен только [Docker Desktop](https://www.docker.com/products/docker-desktop/) (запущенный). Python ставить не нужно.

### Windows — в один клик

Дважды кликните **`start.bat`**. Скрипт сам:

1. проверит, что Docker запущен;
2. создаст `.env` из `.env.example`, если его ещё нет;
3. соберёт и поднимет контейнеры;
4. дождётся ответа API и откроет Swagger в браузере.

### Любая ОС — вручную

```bash
cp .env.example .env          # Windows PowerShell: Copy-Item .env.example .env
docker compose up -d --build
```

Откройте http://localhost:8080/docs.

> Пароль базы задаётся в `.env` (`POSTGRES_PASSWORD`). Файл `.env` в git не попадает — в репозитории лежит только шаблон `.env.example`.

## Что где работает

| Сервис | Адрес с вашего компьютера | Адрес изнутри Docker |
| --- | --- | --- |
| API (Swagger) | http://localhost:8080/docs | `todo-backend:8000` |
| PostgreSQL 18 | `localhost:5432`, пользователь `postgres` | `postgres:5432` |
| Redis 8 | `localhost:6379` | `redis:6379` |

Данные Postgres хранятся в томе `postgres_data` и переживают перезапуск и `docker compose down`.

## API

Базовый URL: `http://localhost:8080`

| Метод | Путь | Тело запроса | Ответ |
| --- | --- | --- | --- |
| `GET` | `/tasks` | — | `200` — массив задач (`[]`, если пусто) |
| `POST` | `/tasks` | `{"title": "Сделать ДЗ"}` | `201` — созданная задача |
| `PATCH` | `/tasks/{id}` | `{"title": "..."}` и/или `{"completed": true}` | `200` — обновлённая задача |
| `DELETE` | `/tasks/{id}` | — | `204` — без тела |

Задача:

```json
{ "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "title": "Сделать ДЗ", "completed": false }
```

## Фронтенд (необязательно)

В папке `frontend/` лежит простой веб-интерфейс на Python (FastAPI), который ходит в это API. Запуск:

```bash
python -m venv .venv
.venv\Scripts\pip install fastapi uvicorn      # Linux/macOS: .venv/bin/pip
.venv\Scripts\python -m uvicorn frontend.app:app --port 3000
```

Откройте http://localhost:3000. Адрес API можно поменять переменной `BACKEND_URL` (по умолчанию `http://localhost:8080`).

## Полезные команды

| Команда | Что делает |
| --- | --- |
| `docker compose ps` | Статус сервисов (`healthy`, `exited`) |
| `docker compose logs -f todo-backend` | Логи API |
| `docker compose up -d --build` | Пересобрать после изменений в коде |
| `docker compose exec postgres psql -U postgres` | Консоль PostgreSQL |
| `docker compose exec redis redis-cli` | Консоль Redis (`KEYS *`, `TTL cache:tasks_list`) |
| `docker compose down` | Остановить всё, данные сохранятся |
| `docker compose down -v` | Остановить и **удалить данные** базы |

## Если что-то не работает

| Симптом | Что сделать |
| --- | --- |
| `port is already allocated` | Порт 8080, 5432 или 6379 занят другим контейнером или локальным Postgres/Redis — остановите его (`docker ps`) |
| API не открывается, в `docker compose ps` у `todo-backend` статус `Exited` | Смотрите `docker compose logs todo-backend` |
| `password authentication failed` | Пароль в `.env` поменяли после первого запуска. База помнит старый: верните его или пересоздайте данные через `docker compose down -v` |
| `start.bat` пишет, что Docker не запущен | Запустите Docker Desktop и дождитесь, пока он станет зелёным |

## Структура

```
app/
  main.py              # приложение FastAPI, CORS, создание таблиц
  api/routers/task.py  # эндпоинты /tasks
  api/dependencies.py  # внедрение зависимостей
  services/task.py     # бизнес-логика + кэш
  repositories/task.py # запросы к БД (SQLAlchemy)
  models/              # ORM-модели
  schemas/task.py      # Pydantic-схемы
  cache/redis.py       # обёртка над Redis
  core/config.py       # настройки
  db/sessions.py       # подключение к БД
frontend/app.py        # веб-интерфейс (необязательно)
Dockerfile
docker-compose.yaml
start.bat              # запуск в один клик (Windows)
.env.example           # шаблон переменных окружения
```
