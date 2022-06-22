#!/bin/bash

# ----------------------------------------------------
# Update  für ClubDMX starten 
# ----------------------------------------------------
# Die verschiedenen Möglichkeiten des Updates werden hier ausgewählt
# Auswahl 1: von zip-File oder von Github
# Auswahl 2: OS-Version raspi oder debian
# Auswahl 3: ClubDMX nach Update im Testmodus starten ja/nein
# ----------------------------------------------------
# Das Update funktioniert nur mit Root-Rechten!
# ref: https://askubuntu.com/a/30157/8698

if ! [ "$(id -u)" = 0 ]; then
  echo "Dieses Script muss mit root-Rechten gestartet werden!" 
	exit 1
fi

if [ $SUDO_USER ]; then
    realuser=$SUDO_USER
else
    realuser=$(whoami)
fi
realhome="/home/$realuser"
echo "Real User: $realuser"
echo "User: $USER"


# Konfiguration über Environment-Varialben oder Default-Werte:
codepath="${CLUBDMX_CODEPATH:-$realhome/clubdmx_code}"
roompath="${CLUBDMX_ROOMPATH:-$realhome/clubdmx_rooms}"
gunicornstart="${GUNICORNSTART:-$realhome/.local/bin/gunicorn}"
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
  echo "Verwendung: $0 -o <os_version> -f [github | <zipfile>] [-s test]"
  echo "os_version: raspi oder debian"
  exit 1
fi

# zip oder git?
if [ -z "$ZIPFILE" ]; then
  echo "Die Update-Quelle (git oder <zipfile>) wurde nicht angegeben."
  echo "Verwendung: $0 -o <os_version> -f [github | <zipfile>] [-s test]"
  exit 1
fi

# Startoption nach Update:
if [ -z "$STARTOPT" ]; then
  echo "Nach dem Update ClubDMX regulär starten."
else
  echo "Nach dem Update ClubDMX im Testmodus starten."
fi

# code-Verzeichnis update:
cd $realhome
if [ -d tmpupdate ]; then
  rm -r tmpupdate
fi
sudo -u $realuser mkdir tmpupdate

if [ "$ZIPFILE" = "github" ]; then
  echo "Update von Github"
  sudo -u $realuser git clone https://github.com/GuntherSe/clubdmx_code.git tmpupdate
  updatesource="tmpupdate/"
else
  if [ -f "$ZIPFILE" ]; then
    echo "Update von $ZIPFILE"
    # Problem: Struktur von ZIP-File kann mit subdir 'clubdmx_code' oder
    # mit subdir 'clubdmx_code-master' oder ohne subdir sein.

    echo A | unzip "$ZIPFILE" -d tmpupdate/
    if [ -d "tmpupdate/clubdmx_code-master" ]; then
      mv "tmpupdate/clubdmx_code-master" "tmpupdate/clubdmx_code"
      updatesource="tmpupdate/clubdmx_code" 
    elif [ -d "tmpupdate/clubdmx_code" ]; then
      updatesource="tmpupdate/clubdmx_code" 
    else
      updatesource="tmpupdate/" 
    fi
  else
    echo "$ZIPFILE nicht gefunden. Update konnte nicht durchgeführt werden."
  fi
# echo "Update Source = $updatesource"
fi

echo "Aktuellen ClubDMX Code entfernen und neuen Code installieren."
rm -r $codepath/app
rm -r $codepath/dmx
rm -r $codepath/scripts
rm -r $updatesource/.git 2> /dev/null
sudo -u $realuser cp -R $updatesource/. $codepath/
rm -r tmpupdate

cd $codepath
dos2unix ./scripts/*.sh
chmod +x ./scripts/*.sh

# Python-Extensions update:
echo "Python Extensions updaten..."
if [ "$OSVERSION" = "raspi" ]; then
  sudo -u $realuser ./scripts/python_setup.sh upgrade $OSVERSION
elif [ "$OSVERSION" = "debian" ]; then
  sudo -u $realuser ./scripts/python_setup.sh upgrade $OSVERSION
else
  echo "$OSVERSION ist keine gültige os_version (raspi oder debian). "
  exit 1
fi

# vor dem Start:
echo "Raum-Verzeichnis für neue Version updaten..."
sudo -u $realuser python3 ./dmx/rooms_check.py $roompath

# ClubDMX neu starten:
if [ -z "$STARTOPT" ]; then
  echo "ClubDMX neu starten."
  echo "j" | ./scripts/nginx_setup.sh
  # systemctl restart clubdmx
  # systemctl restart nginx
else
  echo "ClubDMX im Testmodus mit Rückmeldungen starten."
  sudo -u $realuser ./scripts/app_start.sh stop
  sudo -u $realuser ./scripts/app_start.sh start
fi

