#!/bin/bash

# ----------------------------------------------------
# NGINX für ClubDMX vorbereiten 
# ----------------------------------------------------
# ref: https://askubuntu.com/a/30157/8698

if ! [ "$(id -u)" = 0 ]; then
  echo "Dieses Script muss als root gestartet werden!" 
	exit 1
fi

# Virtualenv Option angegeben?
while [ True ]; do
if [ "$1" = "-v" ]; then
    VIRTUALENV=$2
    shift 2
else
    break
fi
done

if [ $SUDO_USER ]; then
    realuser=$SUDO_USER
else
    realuser=$(whoami)
fi
realhome="/home/$realuser"
echo "Real User: $realuser"
echo "User: $USER"

codepath="${CLUBDMX_CODEPATH:-$realhome/clubdmx_code}"
cd $codepath/scripts

echo "Files vorbereiten..."
if [ -z $VIRTUALENV ]; then
  echo "Virtualenv nicht angegeben."
  sudo -u $realuser python3 nginxfiles.py
else
  echo "Verwende Virtualenv $VIRTUALENV"
  sudo -u $realuser python3 nginxfiles.py $VIRTUALENV
fi

# echo "Files kopieren, benötigt SUDO Rechte!"
cp service.txt /etc/systemd/system/clubdmx.service
cp site.txt /etc/nginx/sites-available/clubdmx
ln -s /etc/nginx/sites-available/clubdmx /etc/nginx/sites-enabled 2> /dev/null
# nginx default-Site löschen
rm /etc/nginx/sites-enabled/default 2> /dev/null

read -p "Den ClubDMX Dienst neu starten (J|N)? <N> " yn
case $yn in
  [Jj]* ) 
    systemctl daemon-reload
    systemctl restart clubdmx
    systemctl enable clubdmx
    systemctl restart nginx
    # Status:
    echo "Statusanzeige mit 'q' beenden"
    systemctl status clubdmx 
    systemctl status nginx
    ;;

  * ) echo "ClubDMX Dienst wurde nicht neu gestartet.";;
esac

read -p "Temporäre Dateien löschen (J|N)? <J>" yn
case $yn in
  [Nn]* ) 
    echo "Temporäre Dateien werden nicht gelöscht."
    ;;

  * ) 
    rm site.txt
    rm service.txt
    ;;
esac

