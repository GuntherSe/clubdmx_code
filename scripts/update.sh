#!/bin/bash

# ----------------------------------------------------
# Update  für ClubDMX starten 
# ----------------------------------------------------
# Die verschiedenen Möglichkeiten des Updates werden hier ausgewählt
# Auswahl 1: von zip-File oder von Github
# Auswahl 2: OS-Version raspi oder debian
# Auswahl 3: ClubDMX nach Update im Testmodus starten ja/nein
# Auswahl 4: Virtual Environment: Wenn angegeben, dann ist es ein 
#    Verzeichnis im Home-Laufwerk, z.B.: .venv
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
while getopts f:o:s:v: flag
do
  case "${flag}" in
    f) ZIPFILE=${OPTARG};;
    o) OSVERSION=${OPTARG};;
    s) STARTOPT=${OPTARG};;
    v) VIRTUALENV=${OPTARG};;
  esac
done

# Betriebssystem ermittlen:
if [ -z "$OSVERSION" ]; then
  echo "Die OS-Version wurde nicht angegeben."
  echo "Verwendung: $0 -o <os_version> -f [github | <zipfile>] [-s test] [-v venv]"
  echo "os_version: raspi oder debian"
  exit 1
fi

# zip oder git?
if [ -z "$ZIPFILE" ]; then
  echo "Die Update-Quelle (git oder <zipfile>) wurde nicht angegeben."
  echo "Verwendung: $0 -o <os_version> -f [github | <zipfile>] [-s test] [-v venv]"
  exit 1
fi

# Virtualenv Option angegeben?

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
    exit 1 
  fi
# echo "Update Source = $updatesource"
fi

echo "Aktuellen ClubDMX Code entfernen und neuen Code installieren."
rm -r $codepath/app
rm -r $codepath/dmx
if [ -d "$codepath/scripts" ]; then
  rm -r $codepath/scripts
fi

rm -r $updatesource/.git 2> /dev/null
sudo -u $realuser cp -R $updatesource/. $codepath/
rm -r tmpupdate

cd $codepath
dos2unix ./scripts/*.sh
chmod +x ./scripts/*.sh

# Python-Extensions installieren:
if [ -z "$VIRTUALENV" ]; then
  echo "Python Extensions installieren..."
else
  echo "Python Extensions in $VIRTUALENV installieren..."
  source $realhome/$VIRTUALENV/bin/activate
fi
if [ "$OSVERSION" = "raspi" ]; then
  ./scripts/python_setup.sh install $OSVERSION
elif [ "$OSVERSION" = "debian" ]; then
  ./scripts/python_setup.sh install $OSVERSION
else
  echo "$OSVERSION ist keine gültige os_version (raspi oder debian). "
  exit 1
fi

# if [ -z "$VIRTUALENV" ]; then
#   echo "Python Extensions installieren..."
# else
#   echo "Python Extensions in $VIRTUALENV installieren..."
#   sudo -u $realuser source $realhome/$VIRTUALENV/bin/activate
# fi
# if [ "$OSVERSION" = "raspi" ]; then
#   sudo -u $realuser ./scripts/python_setup.sh install $OSVERSION
# elif [ "$OSVERSION" = "debian" ]; then
#   sudo -u $realuser ./scripts/python_setup.sh install $OSVERSION
# else
#   echo "$OSVERSION ist keine gültige os_version (raspi oder debian). "
#   exit 1
# fi

# vor dem Start:
echo "Raum-Verzeichnis für neue Version updaten..."
sudo -u $realuser python3 ./dmx/rooms_check.py $roompath

# ClubDMX neu starten:
if [ -z "$STARTOPT" ]; then
  echo "ClubDMX neu starten."
  if [ -z "$VIRTUALENV" ]; then
    echo "j" | ./scripts/nginx_setup.sh
  else
    echo "j" | ./scripts/nginx_setup.sh -v $VIRTUALENV
  fi
  # systemctl restart clubdmx
  # systemctl restart nginx
else
  echo "ClubDMX im Testmodus mit Rückmeldungen starten."
  sudo -u $realuser ./scripts/app_start.sh stop
  if [ -z "$VIRTUALENV" ]; then
    sudo -u $realuser ./scripts/app_start.sh start
  else
    sudo -u $realuser ./scripts/app_start.sh -v $VIRTUALENV start
  fi
fi

