#!/bin/bash

#neon installation on docker

echo 'loading neon-api image...'
docker load < neon-api.tar.gz

echo 'starting neon system container...'
docker-compose up -d
