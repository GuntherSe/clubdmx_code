#!/bin/bash
# ~/clubdmx_code/app_start.sh
# ----------------------------------------------------
# Start der App ClubDMX
# ----------------------------------------------------

# Am Besten auch gleich einen Alias anlegen:
# Die folgende Zeile am Ende von ~/.bashrc anfügen 
# (natürlich ohne '#' am Anfang):
# alias clubdmx='$HOME/clubdmx_code/app_start.sh'
# Anschließend Terminal neu starten

# --- Startoptionen: ----------------------------------
# werden in /etc/environment mit Environment-Variablen festgelegt
# z.B.: in /etc/environment am Ende: export GUNICORNSTART="/usr/bin/gunicorn3 --daemon"
# oder Terminal Start mit Rückeldungen: export GUNICORNSTART="gunicorn"
# -----------------------------------------------------

# Konfiguration über Environment-Varialben oder Default-Werte:
codepath="${CLUBDMX_CODEPATH:-$HOME/clubdmx_code}"
roompath="${CLUBDMX_ROOMPATH:-$HOME/clubdmx_rooms}"
gunicornstart="${GUNICORNSTART:-$HOME/.local/bin/gunicorn}"

cd $codepath
export PYTHONPATH="${PWD}/app:${PWD}/dmx"

case "$1" in
  start)
    echo "Starte ClubDMX zum Testen"
    touch test1running
    $gunicornstart  -b 0.0.0.0:5000  wsgi:app
    # Anmerkung: mit pgrep -fl wsgi.py erhält man die PID
    ;;
    
  service)
    # für den Start als Service
    echo "Starte ClubDMX als Service"
    touch test1running
    $gunicornstart --bind unix:clubdmx.sock -m 007 wsgi:app
    ;;

  stop)
    echo "Stoppe ClubDMX"
    rm test1running 2> /dev/null
    pkill -f gunicorn
    ;;

  update)
    echo "Update ClubDMX"
    echo "Zum Update das Script update.sh verwenden!"
    ;;

  *)
    echo "Verwendung: $0 <start|stop|service>"

    if [ -e test1running ]
    then
        echo "running"
    else
        echo "not running"
    fi
    ;;
esac

exit 0
