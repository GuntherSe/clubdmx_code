#!/bin/bash

# ----------------------------------------------------
# NGINX für ClubDMX vorbereiten 
# ----------------------------------------------------

echo "Script wird von User $USER ausgeführt."
echo "Taste drücken, um fortzufahren."
read i

codepath="${CLUBDMX_CODEPATH:-$HOME/clubdmx_code}"
cd $codepath/scripts

echo "Files vorbereiten..."
python3 nginxfiles.py

# echo "Files kopieren, benötigt SUDO Rechte!"
cp service.txt /etc/systemd/system/clubdmx.service
cp site.txt /etc/nginx/sites-available/clubdmx
ln -s /etc/nginx/sites-available/clubdmx /etc/sites-enabled 2> /dev/null
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

