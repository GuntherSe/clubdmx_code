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
    echo "Starte ClubDMX "
    touch test1running
    $gunicornstart  --daemon -b 0.0.0.0:5000  wsgi:app
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
    rm test1running 2> /dev/null
    pkill -f gunicorn

    echo "Python-Module updaten..."
    # raspi oder debian, default=raspi:
    while getopts f:o: flag
    do
        case "${flag}" in
            f) ZIPFILE=${OPTARG};;
            o) OSVERSION=${OPTARG};;
        esac
    done
    # Betriebssystem ermittlen:
    if [ -z "$OSVERSION" ]; then
      OSVERSION="raspi"
    fi

    ./scripts/python_setup.sh upgrade $OSVERSION

    echo "entpacken und installieren..."
    # Zip-Datei ermittlen:
    if [ -z "$ZIPFILE" ]; then
      ZIPFILE="$HOME/clubdmx_code.zip"
    fi
    
    # Existenz prüfen:
    if [ -f "$ZIPFILE" ]; then
      rm -r app
      rm -r dmx
      # cd /home/pi
      cd ..
      echo A | unzip "$ZIPFILE" 
      # cd /home/pi/clubdmx_code
      cd $codepath

      echo "Skripte ausführbar machen..."
      dos2unix *.sh
      chmod +x *.sh

      echo "Raum-Verzeichnis für neue Version updaten..."
      python3 dmx/rooms_check.py $roompath

      echo "ClubDMX mit Rückmeldungen starten."
      $gunicornstart -b 0.0.0.0:5000  wsgi:app
    
    else
      echo "$ZIPFILE nicht gefunden. Update konnte nicht durchgeführt werden."
    
    fi

    ;;

  *)
    echo "Verwendung: $0 {start|stop|update [-f zipfile] [-o os_version]}"
    echo "zipfile: wenn nicht angegeben, dann wird clubdmx_code.zip verwendet."
    echo "os_version: wenn nicht angegeben, dann wird raspi verwendet."
    echo "für nicht-Standard-Update beide Variablen angeben."

    if [ -e test1running ]
    then
        echo "running"
    else
        echo "not running"
    fi
    ;;
esac

exit 0
