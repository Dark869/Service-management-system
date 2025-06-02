#!/usr/bin/env bash

while read -r linea; do    
	linea=${linea//$'\r'/''} #Borrar errores al hacer el decifrado
	export "$linea"
done < <(ccdecrypt -c .env.cpt)

echo $DB_PASS

python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:7777
