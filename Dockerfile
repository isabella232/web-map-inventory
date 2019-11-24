FROM python:3.7-alpine

LABEL maintainer = "Felix Fennell <felnne@bas.ac.uk>"

# Setup project
WORKDIR /usr/src/app
ENV PYTHONPATH /usr/src/app

# Setup project dependencies
COPY requirements.txt /usr/src/app/
RUN apk add --no-cache libxslt-dev libffi-dev libressl-dev && \
    apk add --no-cache --virtual .build-deps --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing --repository http://dl-cdn.alpinelinux.org/alpine/edge/main build-base && \
    apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing --repository http://dl-cdn.alpinelinux.org/alpine/edge/main proj-dev proj-util && \
    pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

# Setup runtime
ENTRYPOINT []
ENV FLASK_ENV production
