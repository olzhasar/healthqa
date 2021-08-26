#!/bin/sh

pipenv run alembic -x data=true upgrade head
pipenv run gunicorn -c server/gunicorn.conf.py
