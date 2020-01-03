#!/usr/bin/env bash

set -e

podman run --rm=true --tty --interactive --privileged --user=root --volume /users/geoweb/.config/web-map-inventory/:/home/geoweb/.config/web-map-inventory/:rw docker-registry.data.bas.ac.uk/magic/web-map-inventory/deploy:stable "$@"
