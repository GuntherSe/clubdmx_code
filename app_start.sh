#!/bin/bash
# ~/clubdmx_code/app_start.sh
# ----------------------------------------------------
# Start der App ClubDMX
# ----------------------------------------------------

# Am Besten auch gleich einen Alias anlegen:
# Die folgende Zeile am Ende von /home/pi/.bashrc anfügen 
# (natürlich ohne '#' am Anfang):
# alias clubdmx='/home/pi/clubdmx_code/app_start.sh'
# Anschließend Terminal neu starten

# --- Startoptionen: ----------------------------------
# werden in /etc/environment mit Environment-Variablen festgelegt
# z.B.: in /etc/environment am Ende: export GUNICORNSTART="/usr/bin/gunicorn3 --daemon"
# oder Terminal Start mit Meldung: export GUNICORNSTART="gunicorn"
# -----------------------------------------------------

# Konfiguration über Environment-Varialben oder Default-Werte:
codepath="${CLUBDMX_CODEPATH:-/home/pi/clubdmx_code}"
roompath="${CLUBDMX_ROOMPATH:-/home/pi/clubdmx_rooms}"
gunicornstart="${GUNICORNSTART:-/home/pi/.local/bin/gunicorn --daemon}"


cd $codepath
export PYTHONPATH="${PWD}/app:${PWD}/dmx"

case "$1" in
  start)
    echo "Starte ClubDMX "
    touch test1running

    $gunicornstart  -b 0.0.0.0:5000  wsgi:app
    # Anmerkung: mit pgrep -fl wsgi.py erhält man die PID
	
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
    ./python_setup.sh

    echo "entpacken und installieren..."
    # Zip-Datei ermittlen:
    if [ -z "$2" ]; then
      ZIPFILE="/$HOME/clubdmx_code.zip"
    else
      ZIPFILE="$2"
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
      gunicorn -b 0.0.0.0:5000  wsgi:app
    
    else
      echo "$ZIPFILE nicht gefunden. Update konnte nicht durchgeführt werden."
    
    fi

    ;;

  *)
    echo "Verwendung: ~/clubdmx_code/app_start.sh {start|stop|update [zipfile]}"
    if [ -e test1running ]
    then
        echo "running"
    else
        echo "not running"
    fi
    ;;
esac

exit 0
