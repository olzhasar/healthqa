FROM python:3.9-slim-buster

RUN pip install pipenv

COPY ./Pipfile ./Pipfile.lock /

RUN pipenv install --deploy

ENV PIPENV_PIPFILE=/Pipfile
ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY ./docker-entrypoint.sh /
RUN chmod +x docker-entrypoint.sh

COPY /src /app

CMD ["/docker-entrypoint.sh"]
