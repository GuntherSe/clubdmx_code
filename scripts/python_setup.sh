#!/bin/bash

# ----------------------------------------------------
# Python für ClubDMX vorbereiten 
# und/oder aktuellen Python Extension Status ermitteln
# ----------------------------------------------------

# Requirement-Datei angegeben?
# diese Terminologie ist vorgesehen: require_'version'.txt 
# 'version' ist die OS-Version, in der Python installiert ist

# Falls eine Virtual Environment verwendet wird, dann muss diese vor dem
# Ausführen dieses Skripts aktiviert werden!

# Vor dem Ausführen des Scripts ins Code-Verzeichnis wechseln!
# codepath="${CLUBDMX_CODEPATH:-$HOME/clubdmx_code}"
# cd $codepath

# NICHT vergessen: .venv aktivieren!

# check venv:
which python3

if [ -z "$2" ]; then
  REQFILE="./scripts/requirements.txt"
else
  REQFILE="./scripts/require_$2.txt"
fi
# echo "reqfile: $REQFILE"   

case "$1" in
  freeze)
  echo "Status der Python Extensions sichern. Sichere in $REQFILE."
  # Erweiterungen abspeichern:
  pip3 freeze > $REQFILE
  ;;

  install)
  echo "Python Extensions installieren. Verwende $REQFILE."
  # setup Python mit den nötigen Erweiterungen:
  python3 -m pip  install -r $REQFILE
  ;;

  upgrade)
  # Upgrade:
  echo "Python Extensions upgrade. Verwende $REQFILE."
  python3 -m pip  install -r $REQFILE --upgrade
  ;;

  *)
  echo "Verwendung: $0 {freeze|install|upgrade [require_<name>.txt] }"
  echo "<name> bezeichnet die OS-Version. (raspi oder debian)"
  ;;

esac

exit 0
