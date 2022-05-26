
# ClubDMX neu installieren

ClubDMX ist in Python programmiert und ist im Wesentlichen Plattform-unabhängig. Eine Installation kann somit auf verschiedenen Betriebssystemen erfolgen. Ich habe es auf Windows 10 und auf verschiedenen Linux-Versionen installiert. Zur Installation auf einem MacOS kann ich leider nichts sagen. In der folgenden Anleitung ist auf den Raspberry PI Bezug genommen, zur Installation auf andere Betriebssysteme gibt es entsprechende Hinweise in den einzelnen Abschnitten.


## Image und Basics (Raspberry PI)

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

### Debian Installation:

Zur Installation von Debian ist nichts spezielles anzumerken. Download des Installers von https://www.debian.org/index.en.html und los gehts. dos2unix ist vorläufig das einzige zusätzliche Paket, das zu installieren ist (siehe oben).

### Windows Installation: 

Hier gibt es keine Anleitung zur Installation von Windows. Wir gehen mal davon aus, dass Windows bereits installiert ist.

## OLA

OLA steht für **Open Lighting Architecture** und es stellt die Verbindung zwischen ClubDMX und der DMX Hardware bzw. der Ethernet Schnittstellen her. OLA läuft auf Linux (und auf MacOS, aber dazu kann ich keine Informationen liefern). Die folgenden Installationsschritte gelten also für Raspberry und Debian.

Zur Installation von OLA gibt es zwei Möglichkeiten: Die Paket-Installation einer ziemlich sicher älteren Version mit apt-get und die Installation der neuesten Version von Github.

### Paketinstallation mit apt-get

    sudo nano /etc/apt/sources.list

hier eintragen:

    #ola:
    deb http://apt.openlighting.org/raspbian wheezy main

Anschließend neu starten.

Nach dem Neustart:

    sudo apt-get install ola

Damit ist OLA installiert

### OLA von Github installieren (die neueste Version)

Hier gibt es meine Dokumentation der einzelnen Schritte:
<https://groups.google.com/g/open-lighting/c/rDIbzhqnWxQ?pli=1>

Siehe meinen Beitrag vom 14.7.2020.

Diese Möglichkeit ist nötig, wenn die neueste Version von OLA gewünscht ist. Ich benötigte die Hardware-Unterstützung des Eurolite-DMX-Adapters USB-DMX512-Pro. Nach Ausführung der in dem Google-Groups Beitrag gelisteten Schritte ist OLA in der neuesten Vrsion installiert.

#### Kontrolle für beide Installationsvarianten: 

im Browser die **OLA Website** aufrufen = 127.0.0.1:9090

hier nachsehen: Plugins -> OSC ->Config Location: /etc/ola/ola-osc.conf. Findet man hier Informationen, dann kann man von einer korrekten Installation ausgehen.

Weiter im Browser auf 127.0.0.1:9090:

    Home -> Add Universe
    Universe ID: 1
    Universe Name: Uni1
    Checkbox anhaken bei erster Zeile OSC Device Input /dmx/universe/%d 

für weitere Universen wiederholen.

Outputs nach persönlicher Hardware-Verfügbarkeit eintragen. Die entsprechenden Hardware-Komponenten müssen angesteckt sein und werden von OLA erkannt.
(Anm: Enttec war erst nach Reboot verfügbar)

### Windows Installation

Da OLA auf Windows nicht läuft, muss eine virtuelle Maschine mit Linux eingerichtet werden. Ich habe dafür VirtualBox und Debian im Einsatz. Das läuft gut. 


## ClubDMX

ClubDMX ist gepackt in der Datei **clubdmx_code.zip**. Diese Datei wird ins Home-Verzeichnis kopiert. Das kann mit **Filezilla** oder einem anderen Programm zum Übertragen der Dateien gemacht werden. Oder vom USB-Stick kopieren.

Anschließend werden die zip-Datei entpackt und die weiteren Installationsschritte ausgeführt:

    unzip clubdmx_code.zip
    cd clubdmx_code

*TODO:* Installation von Github dokumentieren. 

### Verzeichnisse:

Die beiden für ClubDMX nötigen Verzeichnisse sind das Code-Verzeichnis und das Raum-Verzeichnis:

    ~/clubdmx_code
    ~/clubdmx_rooms

Die beiden hier genannten Verzeichnisse sind die Default-Werte. 
Die Verzeichnisse für Code und Räume können abweichend von den Default-Werten beliebig positioniert werden. ClubDMX findet die Verzeichnisse über Environment-Variablen.

    export CLUBDMX_CODEPATH=/home/pi/clubdmx_code
    export CLUBDMX_ROOMPATH=/home/pi/clubdmx_rooms
    export GUNICORNSTART=/home/pi/.local/bin/gunicorn

In den obigen Zeilen stehen die Default-Werte für den User pi. Falls andere Pfade und/oder ein anderer User verwendet werden, dann werden in /etc/environment die entsprechenden Environment-Variablen gesetzt.

In dieser Installations-Anleitung wird die Verwendung der Default-Verzeichnisse angenommen. Für alternative Verzeichnisse werden die angegebenen Befehle entsprechend adaptiert.

### Alias anlegen: 

Für die Standard-Installation kann auf diesen Schritt verzichtet werden. Zu Testzwecken, Programmentwicklung und Fehlersuche erspart die Verwendung eines Alaias einiges an Tippen.
Diese Zeile am Ende von ~/.bashrc anfügen:

    alias clubdmx='$HOME/clubdmx_code/app_start.sh'

### Script Files

Shell Script Files ausführbar machen:

    cd ~/clubdmx_code
    dos2unix *.sh
    chmod +x *.sh

## Python Module

(wir befinden uns im ClubDMX-Codeverzeichnis)

Alle nötigen Module installieren:

Für Installation am Raspberry:

    ./python_setup.sh install raspi

Für Installation am Debian Rechner:

    ./python_setup.sh install debian
 

.env editieren (mit Nano oder anderem Texteditor):

    nano .env

hier eintragen: 

    SECRET_KEY = b”lange+geheime?Zeichenkette” 

(= beliebiger, langer String, NICHT genau dieser)

Nun ist ClubDMX fertig installiert und die Installation kann **getestet** werden, durch Starten von app_start.sh. Wenn wie oben angegeben der Alias angelegt wurde, dann mit folgendem Befehl in einem Terminal:

    clubdmx start

(Ohne das Anlegen eines Alias: *~/clubdmx_code/app_start.sh start*)

### Windows:

Die Python Module werden mit der Batch-Datei **python_steup.bat** installiert. ClubDMX wird mit der Batch-Datei **app_start.bat** gestartet.

    app_start.bat


*TODO*: Batch Dateien aktualisieren.

## Wichtige Anmerkungen:

python_setup.sh kann auch für das Upgrade der Extensions verwendet werden, der entsprechende Befehl lautet für den Raspberry:

    ./python_setup.sh upgrade raspi 

und für Debian:

    ./python_setup.sh upgrade debian 

**app_start.sh**: Der Start der App ist, obwohl die Raspberries bzw. Linux-Rechner nach dem selben Schema installiert wurden, unterschiedlich zu bewerkstelligen. Computer geben eben manchmal Rätsel auf. So liegt zum Beispiel die Extension Gunicorn am Raspberry im Jazzit im Verzeichnis /usr/bin und auf meinem Raspberry in /home/pi/.local/bin. Das muss beim Start der App berücksichtigt werden, indem die Environment-Variable GUNICORNSTART gesetzt wird.

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

Damit entfällt in Raspi-config der Punkt “Wait for Network on Boot”.

## ClubDMX und NGINX

NGINX ist ein Proxy-Server. Mit diesem Server kann ClubDMX im Browser ohne Port-Angabe aufgerufen werden. Also 127.0.0.1 statt 127.0.0.1:5000.

NGINX muss erst installiert werden:

    sudo apt-get install nginx

Falls bei der Installation Fehler auftreten, dann war es vielleicht schon installiert und muss erst vollständig entfernt werden:

    sudo apt-get remove --purge nginx nginx-full nginx-common 
    sudo apt-get install nginx

Kontrolle: Im Browser die IP-Adresse eingeben. Die Nginx Default-Seite sollte sich zeigen.
Hier sind die dazu nötigen Schritte. (siehe: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04-de )

Die systemd-Datei erstellen:

    sudo cp ~/clubdmx_code/etc/clubdmx.service /etc/systemd/system

**Anmerkung:** Hier müssen die Pfade angepasst werden, wenn ClubDMX in einem anderen Verzeichnis installiert wurde. Das gilt auch für die Installation auf einem Debian-Rechner.

Den Dienst starten:

    sudo systemctl start clubdmx
    sudo systemctl enable clubdmx

Der Status kann überprüft werden:

    sudo systemctl status clubdmx

NGINX einrichten:

    sudo cp ~/clubdmx_code/etc/nginx_clubdmx.txt /etc/nginx/sites-available/clubdmx
    sudo ln -s /etc/nginx/sites-available/clubdmx /etc/nginx/sites-enabled
    sudo rm /etc/nginx/sites-enabled/default

Wurde ClubDMX in einem anderen Verzeichnis installiert, dann ist der Kopier-Befehl entsprechend zu ändern.

### Debian Installation:

Die beiden Dateien im Verzeichnis ~/clubdmx_code/etc enthalten Pfadangaben, die auf den User Pi und die Raspi-Installation angepasst sind. Vor Ausführung der oben genannten Schritte müssen diese Pfadangaben korrigiert werden.


Bei Fehlern gibt es hier Kontrollen:

    sudo less /var/log/nginx/error.log überprüft die Nginx-Fehlerprotokolle.
    sudo less /var/log/nginx/access.log überprüft die Nginx-Zugriffsprotokolle.
    sudo journalctl -u nginx überprüft die Nginx-Prozessprotokolle.
    sudo journalctl -u clubdmx überprüft die Gunicorn-Protokolle von ClubDMX.

NGINX testen und neu starten:

    sudo nginx -t
    sudo systemctl restart nginx

Nun ist ClubDMX über NGINX erreichbar.


## ClubDMX update: 

Ich gehe davon aus, dass NGINX im Einsatz ist.
Das neue zip-File wird ins Home-Verzeichnis kopiert, anschließend werden die folgenden Befehle im Terminal ausgeführt.

    unzip clubdmx_code
    cd ~/clubdmx_code
    dos2unix *.sh
    chmod +x *.sh
    sudo systemctl restart clubdmx
    sudo systemctl restart nginx


Im Browser sind nun OLA und ClubDMX aufrufbar.

Die nach der Installation verfügbaren Webseiten:

OLA: 127.0.0.1:9090

ClubDMX: 127.0.0.1

