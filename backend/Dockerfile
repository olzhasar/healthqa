FROM python:3.9-slim-buster

RUN pip install pipenv

COPY ./Pipfile ./Pipfile.lock /

RUN pipenv install --deploy
RUN pipenv install psycopg2-binary --skip-lock

ENV PIPENV_PIPFILE=/Pipfile
ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY ./docker-entrypoint.sh /
RUN chmod +x docker-entrypoint.sh

COPY . /app

CMD ["/docker-entrypoint.sh"]
