#!/bin/bash

if [[ "$(docker images -q govsanc/pst-extractor 2> /dev/null)" == "" ]]; then
    docker pull govsanc/pst-extractor
fi

docker-compose up
