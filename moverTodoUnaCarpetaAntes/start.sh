#!/usr/bin/env bash

while read -r linea; do    
    export "$linea"
done < <(ccdecrypt -c .env.cpt)

docker-compose up -d

