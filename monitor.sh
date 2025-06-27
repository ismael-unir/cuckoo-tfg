#!/bin/bash

DIR_MON="dropped" #directorio a monitorizar
DIR_PRO="dropped/processed" #directorio procesados
COMMAND="$HOME/cuckoo3/venv/bin/cuckoo submit --route-type drop" #comando envío

inotifywait -e create,moved_to -m "$DIR_MON" |
while read -r directory events filename; do
     DT="`date +%Y%m%d%H%M%S`" #fecha y hora actual, se añadirá al archivo
	 #submitir, y luego mover al directorio "dropped"
     C="$COMMAND \"$directory$filename\";mv \"$directory$filename\" \"$DIR_PRO/$DT-$filename\""   
     eval $C  # ejecución del comando
done
