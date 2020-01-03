FROM centos:latest as base

LABEL maintainer = "Felix Fennell <felnne@bas.ac.uk>"

RUN yum -y install python3


FROM base as build

ARG PACKAGE_VERSION

RUN yum -y install python3
RUN python3 -m venv /usr/local/virtualenvs/bas_web_map_inventory
ENV PATH="/usr/local/virtualenvs/bas_web_map_inventory/bin:$PATH"

COPY *.whl /tmp/
RUN pip install --upgrade pip
RUN pip install --index-url https://test.pypi.org/simple/ --extra-index-url=https://pypi.org/simple/ --find-links=file:///tmp/ $PACKAGE_VERSION

FROM base as deploy

LABEL maintainer = "Felix Fennell <felnne@bas.ac.uk>"

RUN yum -y install python3

RUN adduser geoweb
USER geoweb

COPY catalog.xml /etc/xml/catalog
COPY --chown=geoweb:geoweb --from=build /usr/local/virtualenvs/bas_web_map_inventory /usr/local/virtualenvs/bas_web_map_inventory
COPY --chown=geoweb:geoweb manage.py /home/geoweb/
ENV PATH="/usr/local/virtualenvs/bas_web_map_inventory/bin:$PATH"
ENV FLASK_APP=/home/geoweb/manage.py
ENV FLASK_ENV=production
ENV LOG_FILE_PATH=/tmp/app.log
ENV APP_ENABLE_FILE_LOGGING=false

WORKDIR /home/geoweb/.config/web-map-inventory
ENTRYPOINT ["flask"]
