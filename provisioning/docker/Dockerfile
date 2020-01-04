FROM python:3.6-alpine as base

LABEL maintainer = "Felix Fennell <felnne@bas.ac.uk>"

RUN apk add --no-cache libxslt-dev libffi-dev libressl-dev libxml2-utils coreutils git && \
    apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/community --repository http://dl-cdn.alpinelinux.org/alpine/edge/main proj-dev proj-util


FROM base as build

ARG PACKAGE_VERSION

RUN python3 -m venv /usr/local/virtualenvs/bas_web_map_inventory
ENV PATH="/usr/local/virtualenvs/bas_web_map_inventory/bin:$PATH"

COPY wheelhouse/ /tmp/wheelhouse/
ADD http://bsl-repoa.nerc-bas.ac.uk/magic/v1/libraries/python/wheels/linux_x86_64/cp36m/pyproj-2.4.2.post1-cp36-cp36m-linux_x86_64.whl http://bsl-repoa.nerc-bas.ac.uk/magic/v1/libraries/python/wheels/linux_x86_64/cp36m/lxml-4.4.2-cp36-cp36m-linux_x86_64.whl /tmp/wheelhouse/
RUN pip install --index-url https://test.pypi.org/simple/ --extra-index-url=https://pypi.org/simple/ --find-links=file:///tmp/wheelhouse $PACKAGE_VERSION


FROM base as run

ENV PATH="/usr/local/virtualenvs/bas_web_map_inventory/bin:$PATH"
ENV FLASK_APP=/home/geoweb/manage.py
ENV FLASK_ENV=production
ENV LOG_FILE_PATH=/tmp/app.log
ENV APP_ENABLE_FILE_LOGGING=false

RUN adduser -D geoweb

COPY --from=build /usr/local/virtualenvs/bas_web_map_inventory /usr/local/virtualenvs/bas_web_map_inventory
COPY catalog.xml /etc/xml/catalog
COPY --chown=geoweb:geoweb manage.py $FLASK_APP

USER geoweb
WORKDIR /home/geoweb/.config/web-map-inventory
ENTRYPOINT ["flask"]
