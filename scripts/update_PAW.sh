#!/bin/bash

# ----------------------------------------------------
# Update  für ClubDMX am PYTHONANYWHERE Server
# ----------------------------------------------------
# Die verschiedenen Möglichkeiten des Updates werden hier ausgewählt
# von zip-File clubdmx_code-master
# ----------------------------------------------------

echo "User: $USER"

codepath="$HOME/clubdmx_code"
roompath="$HOME/clubdmx_rooms"
# cd $codepath

ZIPFILE="$1"

if [ -z "$ZIPFILE" ]; then
  echo "Die Update-Quelle (<zipfile>) wurde nicht angegeben."
  echo "Verwendung: $0 <zipfile>] "
  exit 1
fi

# code-Verzeichnis update:
cd $realhome
if [ -d tmpupdate ]; then
  rm -r tmpupdate
fi
mkdir tmpupdate

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

echo "Aktuellen ClubDMX Code entfernen und neuen Code installieren."
rm -r $codepath/app
rm -r $codepath/dmx
if [ -d "$codepath/scripts" ]; then
  rm -r $codepath/scripts
fi

rm -r $updatesource/.git 2> /dev/null
cp -R $updatesource/. $codepath/
rm -r tmpupdate

cd $codepath
dos2unix ./scripts/*.sh
chmod +x ./scripts/*.sh


# vor dem Start:
echo "Raum-Verzeichnis für neue Version updaten..."
python3 ./dmx/rooms_check.py $roompath

