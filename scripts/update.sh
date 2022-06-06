#!/bin/bash

# ----------------------------------------------------
# Update  für ClubDMX starten 
# ----------------------------------------------------
# Die verschiedenen Möglichkeiten des Updates werden hier ausgewählt
# Auswahl 1: von zip-File oder von Github
# Auswahl 2: OS-Version raspi oder debian
# Auswahl 3: ClubDMX nach Update im Testmodus starten ja/nein

# Konfiguration über Environment-Varialben oder Default-Werte:
codepath="${CLUBDMX_CODEPATH:-$HOME/clubdmx_code}"
roompath="${CLUBDMX_ROOMPATH:-$HOME/clubdmx_rooms}"
gunicornstart="${GUNICORNSTART:-$HOME/.local/bin/gunicorn}"
cd $codepath

# Kommandozeilenparameter prüfen:
while getopts f:o:s: flag
do
  case "${flag}" in
    f) ZIPFILE=${OPTARG};;
    o) OSVERSION=${OPTARG};;
    s) STARTOPT=${OPTARG};;
  esac
done

# Betriebssystem ermittlen:
if [ -z "$OSVERSION" ]; then
  echo "Die OS-Version wurde nicht angegeben."
  echo "Verwendung: $0 -o <os_version> -f [git | <zipfile>] [-s test]"
  echo "os_version: raspi oder debian"
  exit 1
fi

# zip oder git?
if [ -z "$ZIPFILE" ]; then
  echo "Die Update-Quelle (git oder <zipfile>) wurde nicht angegeben."
  echo "Verwendung: $0 -o <os_version> -f [git | <zipfile>] [-s test]"
  exit 1
fi

# Startoption nach Update:
# zip oder git?
if [ -z "$STARTOPT" ]; then
  echo "Nach dem Update ClubDMX regulär starten."
else
  echo "Nach dem Update ClubDMX im Testmodus starten."
fi

# code-Verzeichnis update:
if [ "$ZIPFILE" = "git" ]; then
  echo "Update von GIT"
  git clone https://github.com/GuntherSe/clubdmx_code.git $codepath
else
  if [ -f "$ZIPFILE" ]; then
    echo "Update von $ZIPFILE"
    # Problem: Struktur von ZIP-File kann mit subdir 'clubdmx_code' oder
    # mit subdir 'clubdmx_code-master' oder ohne subdir sein.

    cd ..
    
    if [ -d tmpupdate ]; then
      rm -r tmpupdate
    fi
    mkdir tmpupdate
    # cd $codepath
    echo A | unzip "$ZIPFILE" -d tmpupdate/
    if [ -d "tmpupdate/clubdmx_code-master" ]; then
      mv "tmpupdate/clubdmx_code-master" "tmpupdate/clubdmx_code"
      updatesource="tmpupdate/clubdmx_code" 
    elif [ -d "tmpupdate/clubdmx_code" ]; then
      updatesource="tmpupdate/clubdmx_code" 
    else
      updatesource="tmpupdate/" 
    fi
    echo "Update Source = $updatesource"

    rm -r $codepath/app
    rm -r $codepath/dmx
    rm -r $codepath/scripts

    cp -R $updatesource/. $codepath/
    rm -r tmpupdate

  else
    echo "$ZIPFILE nicht gefunden. Update konnte nicht durchgeführt werden."
  
  fi
fi

cd $codepath
dos2unix ./scripts/*.sh
chmod +x ./scripts/*.sh

# Python-Extensions update:
echo "Python Extensions updaten..."
if [ "$OSVERSION" = "raspi" ]; then
  ./scripts/python_setup.sh upgrade $OSVERSION
elif [ "$OSVERSION" = "debian" ]; then
  ./scripts/python_setup.sh upgrade $OSVERSION
else
  echo "$OSVERSION ist keine gültige os_version (raspi oder debian). "
  exit 1
fi

# vor dem Start:
echo "Raum-Verzeichnis für neue Version updaten..."
python3 ./dmx/rooms_check.py $roompath

# ClubDMX neu starten:
if [ -z "$STARTOPT" ]; then
  echo "ClubDMX neu starten."
else
  echo "ClubDMX im Testmodus mit Rückmeldungen starten."
  ./scripts/app_start.sh stop
  ./scripts/app_start.sh start
fi

