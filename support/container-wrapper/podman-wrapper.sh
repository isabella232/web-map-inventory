#!/usr/bin/env bash

set -e

blue=$(tput setaf 4)
normal=$(tput sgr0)

printf "%40s\n\n" "${blue}Note: This command was run inside a container.${normal}"

podman run --rm=true --tty --interactive --user=root --volume /users/geoweb/.config/web-map-inventory/:/home/geoweb/.config/web-map-inventory/:rw docker-registry.data.bas.ac.uk/magic/web-map-inventory/deploy:stable "$@"
