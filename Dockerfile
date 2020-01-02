FROM python:3.6-alpine

LABEL maintainer = "Felix Fennell <felnne@bas.ac.uk>"

WORKDIR /usr/src/app
ENV PYTHONPATH /usr/src/app
ENV POETRY_VIRTUALENVS_CREATE false

# Setup project dependencies
COPY support/xml-schemas/catalogue.xml /etc/xml/catalog
COPY poetry.lock pyproject.toml /usr/src/app/
RUN apk add --no-cache libxslt-dev libffi-dev libressl-dev libxml2-utils coreutils && \
    apk add --no-cache --virtual .build-deps --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing --repository http://dl-cdn.alpinelinux.org/alpine/edge/main build-base && \
    apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/community --repository http://dl-cdn.alpinelinux.org/alpine/edge/main proj-dev proj-util git && \
    pip install --upgrade pip && \
    pip install --no-cache-dir poetry==1.0.0 && \
    poetry update --no-interaction --no-ansi && \
    poetry install --no-root --no-interaction --no-ansi && \
    apk --purge del .build-deps

# Setup runtime
RUN adduser -D app && \
    mkdir -p /var/log/app && \
    chown app:root /usr/src/app /var/log/app

ENV FLASK_ENV development

USER app
ENTRYPOINT []
