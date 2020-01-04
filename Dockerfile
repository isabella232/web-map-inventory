FROM python:3.6-alpine as base

LABEL maintainer = "Felix Fennell <felnne@bas.ac.uk>"

ENV APPPATH=/usr/src/app/
ENV PYTHONPATH=$APPPATH

RUN mkdir $APPPATH
WORKDIR $APPPATH

RUN apk add --no-cache libxslt-dev libffi-dev libressl-dev libxml2-utils coreutils git && \
    apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/community --repository http://dl-cdn.alpinelinux.org/alpine/edge/main proj-dev proj-util


FROM base as build

RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing --repository http://dl-cdn.alpinelinux.org/alpine/edge/main build-base
RUN python3 -m venv /usr/local/virtualenvs/bas_web_map_inventory
ENV PATH="/usr/local/virtualenvs/bas_web_map_inventory/bin:$PATH"

# pre-install known wheels to save time
ADD http://bsl-repoa.nerc-bas.ac.uk/magic/v1/libraries/python/wheels/linux_x86_64/cp36m/pyproj-2.4.2.post1-cp36-cp36m-linux_x86_64.whl http://bsl-repoa.nerc-bas.ac.uk/magic/v1/libraries/python/wheels/linux_x86_64/cp36m/lxml-4.4.2-cp36-cp36m-linux_x86_64.whl /tmp/wheelhouse/
RUN pip install --no-index --find-links=file:///tmp/wheelhouse lxml==4.4.2 pyproj==2.4.2.post1

COPY pyproject.toml poetry.toml poetry.lock $APPPATH
RUN pip install --no-cache-dir poetry==1.0.0
RUN poetry update --no-interaction --no-ansi
RUN poetry install --no-root --no-interaction --no-ansi


FROM base as run

ENV PATH="/usr/local/virtualenvs/bas_web_map_inventory/bin:$PATH"
ENV FLASK_APP=/usr/src/app/manage.py
ENV FLASK_ENV=development
ENV LOG_FILE_PATH=/tmp/app.log
ENV APP_ENABLE_FILE_LOGGING=false

COPY support/xml-schemas/catalogue.xml /etc/xml/catalog
COPY --from=build /usr/local/virtualenvs/bas_web_map_inventory/ /usr/local/virtualenvs/bas_web_map_inventory/

RUN adduser -D geoweb
RUN chown geoweb:root $APPPATH
USER geoweb
ENTRYPOINT []
