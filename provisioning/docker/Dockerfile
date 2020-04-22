FROM python:3.8-alpine as base

LABEL maintainer = "Felix Fennell <felnne@bas.ac.uk>"

RUN apk add --no-cache libxslt-dev libffi-dev libressl-dev libxml2-utils coreutils git proj-dev proj-util


FROM base as build

ARG PACKAGE_VERSION
ENV APPVENV=/usr/local/virtualenvs/bas_web_map_inventory

RUN python3 -m venv $APPENV
ENV PATH="$APPVENV/bin:$PATH"

COPY wheelhouse/ /tmp/wheelhouse/
ADD http://bsl-repoa.nerc-bas.ac.uk/magic/v1/libraries/python/wheels/linux_x86_64/cp38m/lxml-4.5.0-cp38-cp38-linux_x86_64.whl http://bsl-repoa.nerc-bas.ac.uk/magic/v1/libraries/python/wheels/linux_x86_64/cp38m/pyproj-2.6.0-cp38-cp38-linux_x86_64.whl /tmp/wheelhouse/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --index-url https://test.pypi.org/simple/ --extra-index-url=https://pypi.org/simple/ --find-links=file:///tmp/wheelhouse $PACKAGE_VERSION


FROM base as run

ENV APPVENV=/usr/local/virtualenvs/bas_web_map_inventory
ENV PATH="$APPVENV/bin:$PATH"
ENV FLASK_APP=/home/geoweb/manage.py
ENV FLASK_ENV=production
ENV LOG_FILE_PATH=/tmp/app.log
ENV APP_ENABLE_FILE_LOGGING=false

RUN adduser -D geoweb

COPY catalog.xml /etc/xml/catalog
COPY --from=build $APPVENV/ $APPVENV/
COPY --chown=geoweb:geoweb manage.py $FLASK_APP

USER geoweb
WORKDIR /home/geoweb/.config/web-map-inventory
ENTRYPOINT ["flask"]
