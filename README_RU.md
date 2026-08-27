# Take Opt Bot 🤖

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)](https://telegram.org)

Телеграм бот для удобного распределения вариантов, тем проектов и заданий в Telegram-чатах и каналах. Идеальное решение для студентов и рабочих групп, которое избавляет от хаоса в чате и делает процесс распределения честным и организованным.

>**Производственная версия бота доступна для тестирования:**
> [**@take_opt_bot**](https://t.me/take_opt_bot) 🤖

> Активно работающий экземпляр бота, демонстрирующий весь заявленный функционал в реальной среде. Рекомендуем начать с тестирования живой версии перед изучением кода.
***
## 🚀 Быстрый старт

### Предварительные требования

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose)
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

### Установка и запуск

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/andrterrius/takeopt.git
   cd takeopt
   ```

2. **Переименуйте файл .env.example в .env**
   ```bash
   mv .env.example .env
   ```

3. **Установите свои переменные окружения в файле .env**
   ```
    COMMON_BOT_TOKEN=<твой-токен>
    COMMON_ADMINS=[<admin1_uid>, <admin2_uid>]
    POSTGRES_HOST=<твой postgres-ip или postgres-domain>
    POSTGRES_PORT=5432
    POSTGRES_EXTERNAL_PORT=5432
    POSTGRES_USER=user
    POSTGRES_PASSWORD=<твой-postgres-пароль>
    POSTGRES_DB=tgbot
    
    REDIS_HOST=<твой redis-ip или redis-domain>
    REDIS_PORT=6379
    REDIS_PASSWORD=<твой redis-пароль>
    REDIS_USE_REDIS=True
    
    DISTRIBUTION_MAX_CHOICES=97
    DISTRIBUTION_BUTTONS_PER_ROW=5
   ```

4. **Запустите сборку проекта**
    ```
   docker-compose up --build -d

## Краткое пособие для разработчиков 💻

### Структура проекта 🌳

Структура проекта следует представленной архитектуре:

```
├───alembic (alembic миграции)
│   └───versions (версии миграций)
│
├───locales (локали переводов)
│   └───ru (переводы на русский язык)
│       └───LC_MESSAGES
└───tgbot
    ├───distribution (основные функции распределения)
    │   └───services (сервисы обработки распределения)
    ├───dquery (функции обработки запроса создания распределения)
    │
    ├───db (база данных)
    │   ├───models (модели базы)
    │   │   └───mixins (миксины базы)
    │   │ 
    │   └───repositories (репозитории управления базой)
    │   
    ├───factory (фабрики создания объектов)
    │
    ├───filters (фильтры хэндлеров)
    │
    ├───handlers (хэндлеры телеграм бота)
    │   ├───admins (хэндлеры для админов)
    │   │
    │   └───users (хэндлеры для пользователей)
    │
    ├───middlewares (промежуточные обработчики middlewares)
    │   ├───inner (внутренние обработчики)
    │   │
    │   └───outer (внешние обработчики)
    │ 
    ├───misc (вспомогательные функции)
    │
    └───services (глобальные сервисы)
```
### Локализация 📝
**В структуру бота заложена возможность добавлять новые 
локализации для текстов, по умолчанию установлен русский язык в dispatcher middleware**

При каждой сборке контейнера автоматически компилируются все переводы.

Обновление новых добавленных текстов в исходном коде текстов и сохранение в messages.pot
```bash
pybabel extract -k _ -o locales/messages.pot .
pybabel update -i locales/messages.pot -d locales
```

### Миграция базы данных 🚘
**Автоматическая миграция на основе моделей**

```bash
alembic revision --autogenerate -m "commit"
```

Новая версия миграции применяется при сборке/пересборке проекта в docker-entrypoint.sh

**Ручное применение миграции**
```bash
alembic upgrade head
```

### Зависимости Python 🐍
**Проект работает с Poetry, поэтому по мере подключения новых библиотек, для обновления зависимостей необходимо выполнить команду**

```bash
pip install poetry
poetry update
```