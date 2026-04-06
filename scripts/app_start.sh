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

# Virtual Environment:
# kann mit der Option -v angegeben werden, das ist dann ein Subdir im HOME-Verzeichnis

# Konfiguration über Environment-Varialben oder Default-Werte:
codepath="${CLUBDMX_CODEPATH:-$HOME/clubdmx_code}"
roompath="${CLUBDMX_ROOMPATH:-$HOME/clubdmx_rooms}"
gunicornstart="${GUNICORNSTART:-$HOME/.local/bin/gunicorn}"

cd $codepath
export PYTHONPATH="${PWD}/app:${PWD}/dmx"

# Virtualenv Option angegeben?
while [ True ]; do
if [ "$1" = "-v" ]; then
    VIRTUALENV=$2
    shift 2
else
    break
fi
done

# Kommando:
COMMAND=( "${@}" )

case "$COMMAND" in

  start)
    echo "Starte ClubDMX zum Testen"
    if [ -z $VIRTUALENV ]; then
      echo "Virtualenv nicht angegeben."
    else
      echo "Verwende Virtualenv $HOME/$VIRTUALENV"
      source $HOME/$VIRTUALENV/bin/activate
      gunicornstart="$HOME/$VIRTUALENV/bin/gunicorn"
    fi
    touch test1running
    $gunicornstart  -w 1 --threads 100 -b 0.0.0.0:5000  wsgi:app
    # Anmerkung: mit pgrep -fl wsgi.py erhält man die PID
    ;;
    
  service)
    # für den Start als Service
    echo "Starte ClubDMX als Service"
    if [ -z $VIRTUALENV ]; then
      echo "Virtualenv nicht angegeben."
      # gunicornstart="/home/gunther/.venv/bin/gunicorn"
    else
      echo "Verwende Virtualenv $HOME/$VIRTUALENV"
      gunicornstart="$HOME/$VIRTUALENV/bin/gunicorn"
    fi
    touch test1running
    # $gunicornstart --bind unix:clubdmx.sock -m 007 wsgi:app
    $gunicornstart  -w 1 --threads 100 --bind 0.0.0.0:5000 wsgi:app
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

  test)
    echo "Zum Basis-Test mit Python (ohne Gunicorn)"
      source $HOME/$VIRTUALENV/bin/activate
      export LOGLEVEL="debug"
      python wsgi.py
    ;;

  *)
    echo "Verwendung: $0 [-v <Virtualenv> ] <start|stop|service> "

    if [ -e test1running ]
    then
        echo "running"
    else
        echo "not running"
    fi
    ;;
esac

exit 0
