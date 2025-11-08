#!/usr/bin/env bash

set -e

pybabel compile -d locales

alembic upgrade head
exec python -m tgbot
