#!/bin/bash

COMPOSE="/usr/local/bin/docker-compose -f docker-compose.yml -f docker-compose.prod.yml --ansi=never"
DOCKER="/usr/bin/docker"

$DOCKER login $1 -u $2 -p $3
$COMPOSE pull
$COMPOSE up -d --attach-dependencies web worker
$COMPOSE up -d --force-recreate --no-deps nginx
