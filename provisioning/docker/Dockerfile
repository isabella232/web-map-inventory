FROM centos:latest as base

LABEL maintainer = "Felix Fennell <felnne@bas.ac.uk>"

RUN yum -y install python3


FROM base as build

RUN yum -y install python3
RUN python3 -m venv /usr/local/virtualenvs/bas_web_map_inventory
ENV PATH="/usr/local/virtualenvs/bas_web_map_inventory/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install -i https://test.pypi.org/simple/ --extra-index-url=https://pypi.org/simple/ bas-web-map-inventory==0.1.0.post32.dev0

FROM base as deploy

LABEL maintainer = "Felix Fennell <felnne@bas.ac.uk>"

RUN yum -y install python3

RUN adduser geoweb
USER geoweb
WORKDIR /home/geoweb

COPY catalog.xml /etc/xml/catalog
COPY --chown=geoweb:geoweb --from=build /usr/local/virtualenvs/bas_web_map_inventory /usr/local/virtualenvs/bas_web_map_inventory
COPY --chown=geoweb:geoweb .flaskenv manage.py /home/geoweb/apps/web-map-inventory/
COPY --chown=geoweb:geoweb .env /home/geoweb/apps/web-map-inventory/
COPY --chown=geoweb:geoweb entrypoint.sh /home/geoweb/apps/bin/web-map-inventory
ENV PATH="/home/geoweb/apps/bin:$PATH";

ENTRYPOINT []
