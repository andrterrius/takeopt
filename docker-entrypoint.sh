#!/usr/bin/env bash

set -e

mkdir -p locales
pybabel extract -k _ -o locales/messages.pot .
pybabel update -i locales/messages.pot -d locales
pybabel compile -d locales

alembic upgrade head
exec python -m tgbot
