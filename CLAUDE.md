# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Vietnamese Telegram bot built with `pyTelegramBotAPI` (telebot). It provides features like gold/silver prices, stock market data, lunar calendar, lottery results, weather, a dice game (Tai Xiu), and scheduled reminders.

## Running the Bot

**Locally:**
```bash
pip install -r requirements.txt
python app.py
```

**Required `.env` file:**
```
BOT_TOKEN = "..."
WEATHER_KEY = "..."
API_KEY_1TOUCH = "..."
VNSTOCK_API_KEY = "..."
API_KEY_ALPHAVANTAGE = "..."
```

**Required `data/chat_ids.json`:**
```json
{
  "reminder_lunch": [],
  "reminder_badminton": [],
  "reminder_tet": [],
  "schedule_aug": [],
  "schedule_silver": []
}
```

## Docker

**Build the base image** (only when `requirements.txt` changes):
```bash
docker build -f Dockerfile.base -t namtiamo/tele-base:latest .
```

**Build app image:**
```bash
docker build --rm --force-rm -t namtiamo/tele:latest .
```

**Run with Docker Compose:**
```bash
docker compose up -d
docker compose logs -f
```

**Update bot:**
```bash
docker pull namtiamo/tele:latest
docker compose down && docker compose up -d
```

## Critical Deployment Note

The `logs/` directory contains both Python source files (`logs.py`, `__init__.py`) AND runtime `.log` files. When deploying to a new server with volume mounts, copy the Python files from the image **before** running docker-compose, otherwise the import will fail:

```bash
docker create --name temp-bot namtiamo/tele:latest
docker cp temp-bot:/app/logs/logs.py ./logs/
docker cp temp-bot:/app/logs/__init__.py ./logs/
docker rm temp-bot
```

## Architecture

### Request Flow
1. `app.py` initializes `TeleBot` and calls `register_handlers(bot)` on each handler module
2. Each handler in `handlers/` calls the corresponding API module in `get_api/`
3. API modules fetch external data and return structured results to handlers
4. Handlers format responses and send them via the bot

### Module Organization
- **`app.py`** — Entry point; registers all handlers and runs `infinity_polling` with reconnect logic
- **`config.py`** — All environment variables and chat IDs loaded here; import from this, not directly from `.env`
- **`handlers/`** — One file per feature; each exports `register_handlers(bot)`
- **`get_api/`** — External API calls isolated here; no Telegram logic
- **`utils/`** — Shared utilities: `json_storage.py` (JSON CRUD), `retry_decorator.py` (`@retry_on_exception`), `scheduler.py` (background threading), `formatters.py` (price/number formatting), `log_helper.py` (user action logging)
- **`logs/logs.py`** — Logger setup; each module gets its own named logger writing to `/app/bot-logs/`
- **`data/`** — Runtime JSON persistence (chat_ids, stock subscriptions, taixiu scores); mounted as Docker volume

### Adding a New Handler
1. Create `get_api/myfeature.py` with API fetch logic
2. Create `handlers/myfeature.py` with a `register_handlers(bot)` function using `@bot.message_handler`
3. Import and call `myfeature.register_handlers(bot)` in `app.py`
4. Add command to the help text in `handlers/help.py`

### Scheduled Tasks
Scheduling is done via `utils/scheduler.py` which uses the `schedule` library in a background thread. Handlers like `handlers/gold.py` and `handlers/stock.py` register scheduled jobs on import when `register_handlers` is called.

### Data Persistence
All JSON data is accessed through `utils/json_storage.py`. Do not read/write `data/*.json` files directly — use the `JSONStorage` helpers.

### Retry Logic
API calls use `@retry_on_exception` from `utils/retry_decorator.py`. Apply this decorator to any function making external HTTP requests.
