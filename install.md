
# ClubDMX neu installieren

ClubDMX ist in Python programmiert und ist im Wesentlichen Plattform-unabhängig. Eine Installation kann somit auf verschiedenen Betriebssystemen erfolgen. Ich habe es auf Windows 10 und auf verschiedenen Linux-Versionen installiert. Zur Installation auf einem MacOS kann ich leider nichts sagen. In der folgenden Anleitung ist auf den Raspberry PI Bezug genommen, zur Installation auf andere Betriebssysteme gibt es entsprechende Hinweise in den einzelnen Abschnitten.


## Image und Basics (Raspberry PI)

Programm Imager von <https://www.raspberrypi.org/downloads/>

Image erzeugen

Raspi mit Bildschirm und Tatatur starten, anschließend Guide ausführen.

Raspi-Config:

    sudo raspi-config
    1 System Options -> S4 Hostname: Pi-Name eintragen (optional)
    1 System Options -> S6 Wait for Network on Boot (sonst ist OLA nicht mit allen Plugins ausgestattet)
    3 Interfacing Options -> P2 SSH enable (wichtig)
    3 Interfacing Options -> P3 VNC enable (optional)
    4 Localisation Options -> L4 WLAN Country (wichtig) 

Anschließend im Terminal:

    sudo apt-get install dos2unix nginx git

dos2unix ist ein Tool zum Umwandeln von Textdateien mit Windows-Zeilenenden in ein Linux-Format.
Siehe: https://www.digitalmasters.info/de/das-zeilenende-unter-linux-windows-und-os-x-im-griff/

NGINX ist ein Proxy-Server, der die ClubDMX-Webseite zur Verfügung stellt. Mehr dazu später.

### Debian Installation:

Zur Installation von Debian ist nichts Spezielles anzumerken. Download des Installers von https://www.debian.org/index.de.html und los gehts. dos2unix ist vorläufig das einzige zusätzliche Paket, das zu installieren ist (siehe oben).

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

Diese Installation ist nötig, wenn die neueste Version von OLA gewünscht ist. Ich benötigte die Hardware-Unterstützung des Eurolite-DMX-Adapters USB-DMX512-Pro. Nach Ausführung der in dem Google-Groups Beitrag gelisteten Schritte ist OLA in der neuesten Vrsion installiert.

#### Kontrolle für beide Installationsvarianten: 

im Browser die **OLA Website** aufrufen = 127.0.0.1:9090

hier nachsehen: Plugins -> OSC -> Config Location: /etc/ola/ola-osc.conf. Findet man hier Informationen, dann kann man von einer korrekten Installation ausgehen.

Weiter im Browser auf 127.0.0.1:9090:

    Home -> Add Universe
    Universe ID: 1
    Universe Name: Uni1
    Checkbox anhaken bei erster Zeile OSC Device Input /dmx/universe/%d 

für weitere Universen wiederholen.

Outputs nach persönlicher Hardware-Verfügbarkeit eintragen. Die entsprechenden Hardware-Komponenten müssen angeschlossen sein und werden von OLA erkannt.
(Anm: Enttec war erst nach Reboot verfügbar)

### Windows Installation

Da OLA auf Windows nicht läuft, muss eine virtuelle Maschine mit Linux eingerichtet werden. Ich habe dafür VirtualBox und Debian im Einsatz. Das läuft gut. 


## ClubDMX

Die hier im Detail beschriebenen Installationsschritte beziehen sich auf eine Linux-Umgebung. Am Ende dieses Abschnitts finden sich Anmerkungen zur Installation auf einem Windows-System.

### Installation von Zip-Datei

ClubDMX ist gepackt in der Datei **clubdmx_code.zip**. Diese Datei wird ins Home-Verzeichnis kopiert. Das kann mit **Filezilla** oder einem anderen Programm zum Übertragen der Dateien gemacht oder vom USB-Stick kopiert werden.

Anschließend werden die zip-Datei entpackt und die weiteren Installationsschritte ausgeführt:

    cd ~
    mkdir clubdmx_code
    unzip clubdmx_code.zip -d clubdmx_code

### Installation von Github

ClubDMX ist auf Github zu finden. Die Installation der neuesten Version ist hier einfach zu machen.

    cd ~
    git clone https://github.com/GuntherSe/clubdmx_code.git clubdmx_code

### Verzeichnisse:

Die beiden für ClubDMX nötigen Verzeichnisse sind das Code-Verzeichnis und das Raum-Verzeichnis:

    ~/clubdmx_code
    ~/clubdmx_rooms

Die beiden hier genannten Verzeichnisse sind die Default-Werte. 
Die Verzeichnisse für Code und Räume können abweichend von den Default-Werten beliebig positioniert werden. ClubDMX findet die Verzeichnisse über Environment-Variablen.

    export CLUBDMX_CODEPATH=/home/pi/clubdmx_code
    export CLUBDMX_ROOMPATH=/home/pi/clubdmx_rooms
    export GUNICORNSTART=/home/pi/.local/bin/gunicorn

In den obigen Zeilen stehen die Default-Werte für den User pi. Falls andere Pfade und/oder ein anderer User verwendet werden, dann werden in /etc/environment die entsprechenden Environment-Variablen gesetzt. Anschließend neu starten.

In dieser Installations-Anleitung wird die Verwendung der Default-Verzeichnisse angenommen. Für alternative Verzeichnisse werden die angegebenen Befehle entsprechend adaptiert.

### Alias anlegen: 

Für die Standard-Installation kann auf diesen Schritt verzichtet werden. Zu Testzwecken, Programmentwicklung und Fehlersuche erspart die Verwendung eines Alaias einiges an Tippen.
Diese Zeile am Ende von ~/.bashrc anfügen:

    alias clubdmx='$HOME/clubdmx_code/scripts/app_start.sh'

### Script Files

Shell Script Files ausführbar machen:

    cd ~/clubdmx_code/scripts
    dos2unix *.sh
    chmod +x *.sh

## Python Module

(wir befinden uns im ClubDMX-Skriptverzeichnis, ~/clubdmx_code/scripts)

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

(Ohne das Anlegen eines Alias: *~/clubdmx_code/scripts/app_start.sh start*)

## Erstes Login in ClubDMX

Die Testversion von ClubDMX wird im Browser unter der aktuellen IP-Adresse und Port 5000 aufgerufen. Vom aktuellen Rechner also mit

    127.0.0.1:5000

Im lokalen Netzwerk kann ClubDMX nun von jedem Computer mit Browser erreicht werden.

Die Berechtigungen in ClubDMX sind benutzerabhängig. Ohne Login sind nur wenige Seiten verfügbar. Um das Anlegen von Benutzern nach einer Neu-Installation zu ermöglichen, ist ein Admin-Konto bereits angelegt. Das Login erfolgt aus der Navigationsleiste mit diesen Daten:

    Benutzername: Administrator
    Passwort: ClubAdmin2021

Für die Benützung von ClubDMX siehe **Erste Schritte** in der Doku. Die Doku ist in ClubDMX integriert und findet sich über die Navigationszeile im HTML- und im PDF-Format.

## Windows Installation:

Die neueste Version von ClubDMX kann mit [Git for Windows](https://gitforwindows.org/) heruntergeladen werden. Ist *Git for Windows* installiert, dann kann in einem beliebigen Verzeichnis - zum Beispiel im persönlichen Dokumente-Ordner - ClubDMX in wenigen Schritten zum Laufen gebracht werden. Voraussetzung ist ein installiertes Python mit Version >= 3.8. Hier sind die Schritte skizziert:

Zuerst wird der Explorer gestartet und ins Dokumente-Verzeichnis gewechselt. Mit Rechtsklick wird ein Git BASH Terminal gestartet. In diesem Terminal: 

    git clone https://github.com/GuntherSe/clubdmx_code clubdmx_code

Anschließend im Explorer ins Verzeichnis clubdmx_code wechseln. Hier mit Rechtsklick eine neue Textdatei mit Namen **.env** erzeugen. Hier eintragen (siehe oben in der Linux-Anleitung):

    SECRET_KEY = b”lange+geheime?Zeichenkette” 

Anschließend ins Verzeichnis scripts wechseln.

Vor dem ersten Start sind die nötigen Python-Module zu installieren, das geschieht mit dem Script **python_setup.bat**. ClubDMX wird mit der Batch-Datei **app_start.bat** gestartet. 

    python_setup.bat
    app_start.bat

Für das erste Login gilt in Windows dieselbe Anleitung wie in der Linux-Installtion beschrieben. Autostart und die weiteren Installationsschritte entfallen in Windows.

## Wichtige Anmerkungen:

python_setup.sh kann auch für das Upgrade der Extensions verwendet werden, der entsprechende Befehl lautet für den Raspberry:

    ./scripts/python_setup.sh upgrade raspi 

und für Debian:

    ./scripts/python_setup.sh upgrade debian 

**app_start.sh**: Der Start der App ist, obwohl die Raspberries bzw. Linux-Rechner nach dem selben Schema installiert wurden, unterschiedlich zu bewerkstelligen. Vermutlich liegt es daran, ob die Installation als root oder als regulärer User gemacht wird.
Das muss beim Start der App berücksichtigt werden, indem die Environment-Variable GUNICORNSTART gesetzt wird.

Zum Testen der Installation im Terminal kann Gunicorn ohne Pfadangabe verwendet werden.

## Autostart:

Falls OLA über GIT installiert wurde, dann muss der Start von OLA in /etc/rc.local eingetragen werden.

    sudo nano /etc/rc.local

hier eintragen vor der letzten Zeile (= exit 0):

    # olad start:
    su pi -c "olad -f" 

Anmerkung: Wenn beim Einschalten auch der Netzwerk-Router hochgestartet wird (z.B. im Jazzit Saal), dann muss der Netzwerk-Dienst mit Zeitverzögerung neu gestartet werden. Dabei kann auch OLA neugestartet werden. Die folgende Zeile wird in /etc/rc.local eingetragen:

    bash -c “sleep 90 && sudo systemctl restart networking && curl http://127.0.0.1:9090/reload”

Damit entfällt in Raspi-config der Punkt “Wait for Network on Boot”.

## ClubDMX und NGINX

NGINX ist ein Proxy-Server. Über diesen Server wird ClubDMX im Browser aufgerufen.
NGINX wurde bereits installiert (siehe Beginn des Dokuments).
Falls bei der Installation Fehler auftraten, dann war es vielleicht schon installiert und muss erst vollständig entfernt werden:

    sudo apt-get remove --purge nginx nginx-full nginx-common 
    sudo apt-get install nginx

Kontrolle: Im Browser die IP-Adresse 127.0.0.1 eingeben. Die Nginx Default-Seite sollte sich zeigen.
Hier sind die dazu nötigen Schritte im Detail erläutert, siehe: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04-de 

Um die Einrichtung der Verbindung zwischen ClubDMX und NGINX zu erleichtern, habe ich das Script **nginx_setup.sh** geschrieben. Mit diesem Script werden die nötigen Systemdateien abhängig von User und Code-Verzeichnis erzeugt und installiert. Dazu sind root-Rechte nötig.

Falls ClubDMX noch im Test läuft, dann beenden mit:

    clubdmx stop

Nun wird der Start von ClubDMX mit NGINX vorbereitet:

    sudo ./scripts/nginx_setup.sh

Bei Fehlern gibt es hier Kontrollen:

    sudo less /var/log/nginx/error.log überprüft die Nginx-Fehlerprotokolle.
    sudo less /var/log/nginx/access.log überprüft die Nginx-Zugriffsprotokolle.
    sudo journalctl -u nginx überprüft die Nginx-Prozessprotokolle.
    sudo journalctl -u clubdmx überprüft die Gunicorn-Protokolle von ClubDMX.

Nun ist ClubDMX über NGINX erreichbar.


## ClubDMX update: 

Für das Update von ClubDMX gibt es ein Shell Script, **update.sh**. Da Änderungen in diesem Script in einer neueren Version von ClubDMX möglich sind, sollte zuerst 
das aktuelle **update.sh** verfügbar gemacht werden, das auf Github zu finden ist:

https://github.com/GuntherSe/clubdmx_code/blob/master/scripts/update.sh

Hier auf den Button *Raw* klicken, anschließend Rechtsklick, *Seite speichern unter...* auswählen und im Home-Verzeichnis abspeichern. Damit ist die neueste Version des Update-Skripts verfügbar. Anschließend werden die folgenden Befehle im Terminal ausgeführt. **update.sh** benötigt einige Parameter zur korrekten Ausführung:

-f: Hier muss der Name eines ZIP-Files oder *github* als Quelle angegeben werden

-o: Hier muss das Betriebssystem angegeben werden, entweder *raspi* oder *debian*. 

-s: Hier kann die Startoption festgelegt werden. Wird dieser Parameter weggelassen (das ist der Standard), dann wird ClubDMX über NGINX ausgeführt. Falls Probleme beim Update auftreten sollten, dann bitte **update.sh** mit der Startoption -s test erneut ausführen. Damit wird ClubDMX im Terminal mit Rückmeldungen gestartet und Fehler können lokalisiert werden.

Das Update wird nun für den Raspberry mit folgenden Befehlen im Terminal durchgeführt:

    cd ~
    dos2unix update.sh
    chmod +x update.sh
    sudo ./update.sh -f github -o raspi

Im Browser sind nun OLA und ClubDMX aufrufbar.

Die nach der Installation verfügbaren Webseiten:

OLA: 127.0.0.1:9090

ClubDMX: 127.0.0.1

Wenn die Startoption *test* gewählt wurde (im Terminal mit dem Befehl *./update.sh -f github -o raspi -s test*), dann ist ClubDMX im Browser hier zu finden:

127.0.0.1:5000

