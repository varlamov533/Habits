# Habit Tracker API (FastAPI)

Простой и быстрый API для отслеживания привычек. Позволяет создавать пользователей, ставить цели (привычки) и фиксировать их выполнение (чекины).

## 🛠 Технологии
*   **Python 3.11**
*   **FastAPI** — асинхронный веб-фреймворк.
*   **SQLAlchemy 2.0 (Async)** — работа с базой через `asyncpg`.
*   **PostgreSQL** — основное хранилище.
*   **Docker & Docker Compose** — быстрая развертка всей инфраструктуры.
*   **Pydantic** — валидация данных.

## 🚀 Быстрый запуск

### 1. Клонирование репозитория и запуск docker compose

```
git clone https://github.com/varlamov533/Habits.git
cd Habits
docker compose up -d
```

Данный сервис был создан по заданию из https://solvit.space/projects/habit_tracker
