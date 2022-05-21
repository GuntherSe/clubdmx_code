
# Raspberry BULLSEYE neu installieren

## Image und Basics

Programm Imager von <https://www.raspberrypi.org/downloads/>

Image erzeugen

Raspi mit Bidschirm und Tatatur starten, anschließend Guide ausführen

Raspi-Config:

    sudo raspi-config
    1 System Options -> S4 Hostname: Pi-Name eintragen (optional)
    1 System Options -> S6 Wait for Network on Boot (sonst ist OLA nicht mit allen Plugins ausgestattet)
    3 Interfacing Options -> I2 SSH enable (wichtig)
    3 Interfacing Options -> I3 VNC enable (optional)

wichtig: 4 Localisation Options: Ländercode + Utf-8, auch Ländercode für Wlan    

    sudo apt-get install dos2unix

dos2unix ist ein Tool zum Umwandeln von Textdateien mit Windows-Zeilenenden in ein Linux-Format.
Siehe: https://www.digitalmasters.info/de/das-zeilenende-unter-linux-windows-und-os-x-im-griff/

## OLA

Zur Installation von OLA gibt es zwei Möglichkeiten: Die Paket-Installation einer ziemlich sicher älteren Version mit apt-get und die Installation der neuesten Version von Github.

### Paketinstallation mit apt-get

    sudo nano /etc/apt/sources.list

hier eintragen:

    #ola:
    deb http://apt.openlighting.org/raspbian wheezy main

anschließend Reboot

nach dem Neustart:

    sudo apt-get install ola

damit ist OLA installiert

### OLA von Github installieren (die neueste Version)

Hier gibt es meine Dokumentation der einzelnen Schritte:
<https://groups.google.com/g/open-lighting/c/rDIbzhqnWxQ?pli=1>

Siehe meinen Beitrag vom 14.7.2020.

Diese Möglichkeit ist nötig, wenn die neueste Version von OLA gewünscht ist. Ich benötigte die Hardware-Unterstützung des Eurolite-DMX-Adapters USB-DMX512-Pro. Nach Ausführung der in dem Google-Groups Beitrag gelisteten Schritte ist OLA in der neuesten Vrsion installiert.

#### Kontrolle für beide Installationsvarianten: 

im Browser die OLA Website aufrufen = 127.0.0.1:9090

hier nachsehen: Plugins -> OSC ->Config Location: /etc/ola/ola-osc.conf

Weiter im Browser auf 127.0.0.1:9090:

    Universes -> Add Universe
    Universe ID: 1
    Universe Name: Uni1
    Checkbox anhaken bei erster Zeile OSC Device Input /dmx/universe/%d 

für weitere Universen wiederholen.

Outputs nach Verfügbarkeit eintragen.
(Anm: Enttec war erst nach Reboot verfügbar)

## ClubDMX

WinSCP oder anderes Programm zum Übertragen der Dateien.
In allen Betriebssystemen kann **Filezilla** verwendet werden.
Oder vom USB-Stick kopieren.

*TODO:* Install von Github dokumentieren. 

### Verzeichnisse:

Die beiden für ClubDMX nötigen Verzeichnisse sind das Programm-Verzeichnis und das Raum-Verzeichnis:

    /home/pi/clubdmx_code
    /home/pi/clubdmx_rooms

Die beiden hier genannten Verzeichnisse sind die Default-Werte für den User pi. 

Die Verzeichnisse für Code und Räume können abweichend von den Default-Werten beliebig positioniert werden. ClubDMX findet die Verzeichnisse über Environment-Variablen.

export CLUBDMX_CODEPATH=/home/pi/clubdmx_code
export CLUBDMX_ROOMPATH=/home/pi/clubdmx_rooms
export GUNICORNSTART=/home/pi/.local/bin/gunicorn

In den obigen Zeilen stehen die Default-Werte. Falls andere Pfade verwendet werden, dann werden in /etc/environment die entsprechenden Environment-Variablen gesetzt.

In dieser Installations-Anleitung wird die Verwendung der Default-Verzeichnisse angenommen. Für alternative Verzeichnisse werden die angegebenen Befehle entsprechend adaptiert.

### Alias anlegen: 

Diese Zeile am Ende von /home/pi/.bashrc anfügen:

    alias clubdmx='/home/pi/clubdmx_code/app_start.sh'

Shell Script Files ausführbar machen:

    cd /home/pi/clubdmx_code
    dos2unix *.sh
    chmod +x *.sh

## Python Module

(wir befinden uns im ClubDMX-Programmverzeichnis)

Alle nötigen Module installieren:

    ./python_setup.sh

.env editieren:

    nano .env

hier eintragen: 

    SECRET_KEY = b”84nrf97vzih47vzha” 

(= beliebiger zufälliger String, NICHT genau dieser)

Terminal öffnen (in WinSCP oder am Raspi direkt) 

    ./app_start.sh start

### Wichtige Anmerkungen:

Die Datei python_setup.sh kann an verschiedene Bedürfnisse angepasst werden. Ich habe hier verschiedene Verwendungsmöglichkeiten reingeschrieben, die mit ‘#’ auskommentiert sind.

python_setup.sh: kann für die erstmalige Installation der Python-Extensions oder für das Upgrade der Extensions verwendet werden.

*TODO:* python_setup.sh mit Kommandozeilen-Parametern formulieren.

app_start.sh: Der Start der App ist, obwohl die Raspberries bzw. Linux-Rechner nach dem selben Schema installiert wurden, unterschiedlich zu bewerkstelligen. Computer geben eben manchmal Rätsel auf. So liegt zum Beispiel die Extension Gunicorn am Raspberry im Jazzit im Verzeichnis /usr/bin und auf meinem Raspberry in /home/pi/.local/bin. Das muss beim Start der App berücksichtigt werden, indem die Environment-Variable GUNICORNSTART gesetzt wird.

Die Pfadangabe ist deshalb wichtig, weil beim im Folgenden beschriebenen Autostart die PATH Variable vom Betriebssystem noch nicht gesetzt ist.

Also: Zum Testen der Installation im Terminal kann Gunicorn ohne Pfadangabe verwendet werden, für den Autostart muss die Pfadangabe verwendet werden. 

## Autostart:

Falls OLA über GIT installiert wurde, dann muss der Start von OLA in /etc/rc.local eingetragen werden.

    sudo nano /etc/rc.local

hier eintragen vor der letzten Zeile (= exit 0):

    # olad start:
    su pi -c "olad -f" 

Anmerkung: Wenn beim Einschalten auch der Netzwerk-Router hochgestartet wird (z.B. im Jazzit Saal), dann muss der Netzwerk-Dienst mit Zeitverzögerung neu gestartet werden. Dabei kann auch OLA neugestartet werden:

    bash -c “sleep 90 && sudo systemctl restart networking && curl http://127.0.0.1:9090/reload”

Damit entfällt in Raspi-config der Punkt “Wait for Network on Boot”

## ClubDMX und NGINX

NGINX ist ein Proxy-Server. Mit diesem Server kann ClubDMX im Browser ohne Port-Angabe aufgerufen werden. Also 127.0.0.1 statt 127.0.0.1:5000.

Die im vorigen Abschnitt beschriebenen Starts für ClubDMX sind ab Version 1.0 geändert. ClubDMX wird nun als Service gestartet und über NGINX aufgerufen. Damit gibt es auch keine Unterschiede zwischen GUI und Kommandozeilen-Start des Raspberry Pi.

NGINX muss erst installiert werden:

    sudo apt-get install nginx

Falls bei der Installation Fehler auftreten, dann war es vielleicht schon installiert und muss erst vollständig entfernt werden:

    sudo apt-get remove --purge nginx nginx-full nginx-common 
    sudo apt-get install nginx

Kontrolle: Im Browser die IP-Adresse eingeben. Die Nginx Default-Seite sollte sich zeigen.
Hier sind die dazu nötigen Schritte. (siehe: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04-de )

Die systemd-Datei erstellen:

    sudo cp ~/clubdmx_code/etc/clubdmx.service /etc/systemd/system

(=eine Zeile!)

Anmerkung: Hier müssen die Pfade angepasst werden, wenn ClubDMX in einem anderen Verzeichnis installiert wurde. 

Den Dienst starten:

    sudo systemctl start clubdmx
    sudo systemctl enable clubdmx

Der Status kann überprüft werden:

    sudo systemctl status clubdmx

NGINX einrichten:

    sudo cp ~/clubdmx_code/etc/nginx_clubdmx.txt /etc/nginx/sites-available/clubdmx

(=eine Zeile!)

    sudo ln -s /etc/nginx/sites-available/clubdmx /etc/nginx/sites-enabled

(=eine Zeile!)

    sudo rm /etc/nginx/sites-enabled/default

Bei Fehlern gibt es hier Kontrollen:

    sudo less /var/log/nginx/error.log überprüft die Nginx-Fehlerprotokolle.
    sudo less /var/log/nginx/access.log überprüft die Nginx-Zugriffsprotokolle.
    sudo journalctl -u nginx überprüft die Nginx-Prozessprotokolle.
    sudo journalctl -u clubdmx überprüft die Gunicorn-Protokolle von ClubDMX.

NGINX testen und neu starten:

    sudo nginx -t
    sudo systemctl restart nginx

Nun ist ClubDMX über NGINX erreichbar.


## Clubdmx update: 

    unzip clubdmx_code
    chmod +x *.sh
    sudo systemctl restart clubdmx
    sudo systemctl restart nginx


Im Browser sind nun OLA und ClubDMX aufrufbar.

OLA: 127.0.0.1:9090
ClubDMX: 127.0.0.1


Update einer bestehenden Installation von ClubDMX
Diese Update-Option ist für bereits installierte Apps geschrieben, für das eine neue Version verfügbar ist. Die neue Version kommt gezippt als clubdmx_code.zip
Die neue Version wird in das Verzeichnis /home/pi kopiert, dann wird 
app_start.sh update
im Terminal ausgeführt.

