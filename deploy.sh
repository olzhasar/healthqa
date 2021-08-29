#!/bin/bash

COMPOSE="/usr/local/bin/docker-compose -f docker-compose.yml -f docker-compose.prod.yml --ansi=never"
DOCKER="/usr/bin/docker"
PROJECT_ROOT="/srv/healthqa"

cd $PROJECT_ROOT

git pull

$DOCKER login $1 -u $2 -p $3
$COMPOSE pull
$COMPOSE up -d app worker
$COMPOSE up -d --force-recreate nginx
