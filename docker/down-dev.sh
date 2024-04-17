#!/usr/bin/env bash
DIR=`dirname "${BASH_SOURCE[0]}"`
FILE="${DIR}/docker-compose-dev.yml"
docker compose -f ${FILE} down