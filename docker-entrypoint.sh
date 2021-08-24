#!/bin/sh

pipenv run alembic upgrade head
pipenv run gunicorn -c server/gunicorn.conf.py
