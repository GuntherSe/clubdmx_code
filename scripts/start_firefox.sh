#!/bin/bash

# Skript zum Start von Firefox im Kiosk-Modus
# benötigt: firefox-esr, xdotool
# Aufruf in: /etc/xdg/lxsession/LXDE-pi/autostart
#   hier in der Zeile vor dem Screensaver mit passendem Pfad eintragen.
#   z.B.: @/home/pi/clubdmx_code/scripts/start_firefox.sh


/bin/sleep 10
sudo -u pi firefox-esr &
xdotool search --sync --onlyvisible --class "firefox" windowfocus key F11 &
