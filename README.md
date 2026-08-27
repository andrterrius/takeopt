# Take Opt Bot 🤖

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)](https://telegram.org)

[RU README](README_RU.md)

A Telegram bot for convenient distribution of variants, project topics, and assignments in Telegram chats and channels. An ideal solution for students and work groups that eliminates chat chaos and makes the distribution process fair and organized.

>**The production version of the bot is available for testing:**
> [**@take_opt_bot**](https://t.me/take_opt_bot) 🤖

> An active bot instance that demonstrates all the claimed functionality in a real environment. We recommend starting by testing the live version before examining the code.
***

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose)
- Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))

### Installation and Launch

1. **Clone the repository**
   ```bash
   git clone https://github.com/andrterrius/takeopt.git
   cd takeopt
   ```

2. **Rename the .env.example file to .env**
   ```bash
   mv .env.example .env
   ```

3. **Set your environment variables in the .env file**
   ```
    COMMON_BOT_TOKEN=<your-token>
    COMMON_ADMINS=[<admin1_uid>, <admin2_uid>]
    POSTGRES_HOST=<your postgres-ip or postgres-domain>
    POSTGRES_PORT=5432
    POSTGRES_EXTERNAL_PORT=5432
    POSTGRES_USER=user
    POSTGRES_PASSWORD=<your-postgres-password>
    POSTGRES_DB=tgbot
    
    REDIS_HOST=<your redis-ip or redis-domain>
    REDIS_PORT=6379
    REDIS_PASSWORD=<your redis-password>
    REDIS_USE_REDIS=True
    
    DISTRIBUTION_MAX_CHOICES=97
    DISTRIBUTION_BUTTONS_PER_ROW=5
   ```

4. **Build and start the project**
    ```
   docker-compose up --build -d

## Developer Quick Guide 💻

### Project Structure 🌳

The project structure follows this architecture:

```
├───alembic (alembic migrations)
│   └───versions (migration versions)
│
├───locales (translation locales)
│   └───ru (Russian translations)
│       └───LC_MESSAGES
└───tgbot
    ├───distribution (core distribution functions)
    │   └───services (distribution processing services)
    │───query (distribution creation query functions)
    │
    ├───db (database)
    │   ├───models (database models)
    │   │   └───mixins (database mixins)
    │   │ 
    │   └───repositories (database management repositories)
    │   
    ├───factory (object creation factories)
    │
    ├───filters (handler filters)
    │
    ├───handlers (telegram bot handlers)
    │   ├───admins (admin handlers)
    │   │
    │   └───users (user handlers)
    │
    ├───middlewares (middleware handlers)
    │   ├───inner (inner middlewares)
    │   │
    │   └───outer (outer middlewares)
    │ 
    ├───misc (auxiliary functions)
    │
    └───services (global services)
```
### Localization  📝
**The bot's structure includes the capability to add new localizations for texts. Russian is set as the default language in the dispatcher middleware.**

Each time the container is built, all translations are automatically compiled.

Updating and extracting new texts added to the source code and saving to messages.pot:

```bash
pybabel extract -k _ -o locales/messages.pot .
pybabel update -i locales/messages.pot -d locales
```

### Database Migration 🚘
**Automatic migration based on models**

```bash
alembic revision --autogenerate -m "commit"
```

The new migration version is applied when building/rebuilding the project in docker-entrypoint.sh

**Manual migration application**
```bash
alembic upgrade head
```

### Python Dependencies 🐍
**The project uses Poetry, so when adding new libraries, update the dependencies by running:**

```bash
pip install poetry
poetry update
```