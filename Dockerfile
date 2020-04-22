FROM python:3.8-alpine as base

LABEL maintainer = "Felix Fennell <felnne@bas.ac.uk>"

ENV APPPATH=/usr/src/app/
ENV PYTHONPATH=$APPPATH

RUN mkdir $APPPATH
WORKDIR $APPPATH

RUN apk add --no-cache libxslt-dev libffi-dev libressl-dev libxml2-utils coreutils git proj-dev proj-util


FROM base as build

ENV APPVENV=/usr/local/virtualenvs/bas_web_map_inventory

RUN apk add build-base
RUN python3 -m venv $APPVENV
ENV PATH="$APPVENV/bin:$PATH"

# pre-install known wheels to save time
ADD http://bsl-repoa.nerc-bas.ac.uk/magic/v1/libraries/python/wheels/linux_x86_64/cp38m/lxml-4.5.0-cp38-cp38-linux_x86_64.whl http://bsl-repoa.nerc-bas.ac.uk/magic/v1/libraries/python/wheels/linux_x86_64/cp38m/pyproj-2.6.0-cp38-cp38-linux_x86_64.whl /tmp/wheelhouse/
RUN pip install --no-index --find-links=file:///tmp/wheelhouse lxml==4.5.0 pyproj==2.6.0

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry==1.0.0

COPY pyproject.toml poetry.toml poetry.lock $APPPATH
RUN poetry update --no-interaction --no-ansi
RUN poetry install --no-root --no-interaction --no-ansi


FROM base as run

ENV APPVENV=/usr/local/virtualenvs/bas_web_map_inventory
ENV PATH="$APPVENV/bin:$PATH"
ENV FLASK_APP=/usr/src/app/manage.py
ENV FLASK_ENV=development
ENV APP_LOG_FILE_PATH=/tmp/app.log
ENV APP_ENABLE_FILE_LOGGING=false

COPY support/xml-schemas/catalogue.xml /etc/xml/catalog
COPY --from=build $APPVENV/ $APPVENV/

RUN adduser -D geoweb
RUN chown geoweb:root $APPPATH && \
    chown geoweb:root -R $APPVENV
USER geoweb

ENTRYPOINT []
