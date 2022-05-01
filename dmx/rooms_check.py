#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Entfernen von 'px'-Endung aus den Feldern Left, Top, Width und Height 
aus allen Stage-Files
- Datenverzeichnis ermitteln
- alle Räume = subdirs untersuchen

Kommt zum Einsatz, wenn in der Datenstruktur Änderungen vorgenommen werden, 
die Auswirkungen auf bestehende Projekte haben. Ist nicht im täglichen Einsatz 
der App eingebunden.
"""
import os
import os.path
import argparse
import csv

from roombaseclass import Roombase
from csvfileclass import Csvfile

def checkstage (path:str):
    """ Änderugen in Version 0.96: kein 'px' Zusatz in den Feldern
    Left, Top, Width, Height
    """
    print (f"Pfad: {path}")
    count = 0
    for entry in os.scandir (path):
        fullname = os.path.join (path, entry.name)
        chk = fullname.lower()
        if chk.endswith (".csv") or chk.endswith (".ccsv"): # .csv oder .ccsv
            csvfile = Csvfile (fullname)
            print (f"check: {csvfile.name()}")
            count = count + 1
            csvcontent = csvfile.to_list ()
            fieldnames = csvfile.fieldnames ()
            lidx = fieldnames.index ("Left")
            tidx = fieldnames.index ("Top")
            widx = fieldnames.index ("Width")
            hidx = fieldnames.index ("Height")

            with open (csvfile.name(), 'w',encoding='utf-8', newline='') as pf:
                writer = csv.writer (pf)

                for line in csvcontent:
                    field = line[lidx]
                    if field.endswith ("px"):
                        line[lidx] = field[:-2]
                        
                    field = line[tidx]
                    if field.endswith ("px"):
                        line[tidx] = field[:-2]

                    field = line[widx]
                    if field.endswith ("px"):
                        line[widx] = field[:-2]

                    field = line[hidx]
                    if field.endswith ("px"):
                        line[hidx] = field[:-2]
                
                    writer.writerow (line)

    print (f"{count} Stage-Dateien wurden gecheckt.")


# --- Main --------------------------------------------------------------------
if __name__ == "__main__":

    room = Roombase ()

    parser = argparse.ArgumentParser(
        description="Bei Programm-Update Räume anpassen")
    parser.add_argument ("root", help="Verzeichnis, das alle Räume beinhaltet.") 
        # z.B.: /home/pi/clubdmx_rooms
    args = parser.parse_args()
    root = args.root

    print (f"Raum-Basisverzeichnis: {root}")

    # alle Räume checken:
    for entry in os.scandir (root):
        if entry.is_dir (follow_symlinks=False):
            fullpath = os.path.join (root, entry.name)
            room.set_path (fullpath)
            stagepath = room.stagepath ()
            checkstage (stagepath)


