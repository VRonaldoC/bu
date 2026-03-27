#!/usr/bin/env bash
pip install -r requirements.txt

printf "1\n" | python3 SCRIPT_PERMISO_DESBLOQUEO.py &
printf "2\n" | python3 SCRIPT_PERMISO_DESBLOQUEO.py &
printf "3\n" | python3 SCRIPT_PERMISO_DESBLOQUEO.py &
printf "4\n" | python3 SCRIPT_PERMISO_DESBLOQUEO.py &

wait
