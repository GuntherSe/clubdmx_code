#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" class Cue
Ein Cue ist eine Sammlung von Attributwerten diverser Heads.
Wird ein Cue ausgeführt (cuelist_to_contrib), werden die Werte an
den Mixer geschickt.

Für alle Attribute wird ein dict geführt: _cuelist

      
"""

import os
import os.path
import time
import csv


# from ola   import OscOla
# from patch import Patch
from contribclass import Contrib
from csvfileclass import Csvfile

class Cue ():
    # global: CUEPATH, cuecount, Contrib
    CUEPATH = ""
    contrib = Contrib()
    init_done = 0
    # cuecount = 0
    
    def __init__(self, patch):
        if Cue.init_done == 0: # nur 1x ausführen
            if Cue.CUEPATH == "":
                path = os.path.dirname(os.path.realpath(__file__))
                self.set_path (path)
            # else: CUEPATH wurde mit set_path bereits gesetzt
            Cue.contrib.set_output_function (self.mixoutput)
            Cue.contrib.set_mix_function (Cue.contrib.cue_mix)
            Cue.contrib.set_sleeptime (0.025) #0.025
            if not os.environ.get ("PYTHONANYWHERE") == "true":
                Cue.contrib.start ()
            Cue.init_done = 1
            # Cue.contrib.start_mixing ()

        self.count = id (self) # eindeutige id für contrib-mix
        self.patch      = patch
        self._cuelist   = [] # Struktur: [[Head1,Att1,Lev1], [Head2,Att2,Lev2], ...]
        self._cuefields = [] # Struktur: ['HeadNr', 'Attr', 'Level']
        self._autoupdate = False # Auto-Update wenn _level == 0
        fname = os.path.join (Cue.CUEPATH, "_neu")
        self.file     = Csvfile (fname)   # Default Cue File Name
        self.filetime = 0.0  # bei get_cuelist aktualisieren (os.path.getmtime)
        self._active  = False  # cue in Contrib eingetragen -> self._active = True
        self._level   = 1.0  # Wert in [0..1]
        self.level    = 0.0  # Zuweisung mit Properties und Eintrag in Contrib
        # zur späteren Verwendung in Fader und Buttons:
        self.text     = ""  # Anzeigetext
        self.location = ""  # in welcher Cue-Gruppe
                            # (cuebuttons, exebuttons1, exebuttons2, 
                            # cuefaders, exefaders)
        # self.line = 0 # Zeilennummer (ab 0) aus csv-Datei
        self.id       = ""  # = location + Zeilennummer (ab 0) in 
                            # CSV-Datei der Cue-Gruppe

    def __del__ (self):
        self.rem_cuemix ()
        # print ("Cue contrib:", self.count)

    def __repr__(self):
        return "<Cue {}, {}>".format (self.count, self.file.shortname())

    def active (self) ->bool:
        """ Einträge in Contrib vorhanden """
        if self._active:
            return True
        else:
            return False

# Pfad ändern:
    @classmethod
    def set_path (cls, newpath) ->None:
        """ Pfad ändern """
        Cue.CUEPATH = os.path.join (newpath, "cue")
        # print ("cuepath: ", Cue.CUEPATH)

# File Methoden: -----------------------------------------------------
    def open (self, fname=""):
        """ Filename, in dem die Cueinformation gespeichert ist
        """
        if fname:
            openname = os.path.join(Cue.CUEPATH, fname)
            self.file.name (openname)
        # else: filename = "_neu"
        self.get_cuelist()


    def get_cuelist (self):
        """ File einlesen

        siehe Patch._get_pdict()
        """
        filename = self.file.name()
        # print ("Cuefile: ", filename)
        
        if os.path.isfile (filename) and \
            os.path.getmtime(filename) > self.filetime:
            self.rem_cuemix() # evtl aktiven Mix entfernen
            self._cuelist = []
            with open (filename, 'r',encoding='utf-8') as pf: # zum Lesen öffnen und einlesen
                reader = csv.DictReader (pf, restval= '')
                self._cuefields = reader.fieldnames
                for row in reader:
                    attribs = [] # zugehörige Attribute
                    for item in reader.fieldnames:
                        attribs.append (row[item])
                    self._cuelist.append (attribs)
            self.verify()
            self.filetime = os.path.getmtime (filename)
        else:
            pass
            # print ("Cuefile nicht gefunden: ", filename)


    def cuelist (self):
        return self._cuelist


    def to_dictlist (self):
        """ _cuelist in dict-Notation

        Struktur: [{'HeadNr'='head-1','Attr'='att-1','Level'='level-1'},
                   {'HeadNr'='head-2','Attr'='att-2','Level'='level-2'},
                    ... ]
        """
        ret = []
        for line in self._cuelist:
            retline = {}
            for i in range (len (line)):
                retline[self._cuefields[i]] = line[i] 
            ret.append (retline)
        return ret


    def line_to_cuelist (self, newline:list):
        """ line in _cuelist integrieren 

        entweder update oder append
        """
        found = 0
        for line in self._cuelist:
            if line[0] == newline [0] and line[1] == newline [1]:
                found = 1
                line[2] = newline[2]
        if not found:
            self._cuelist.append (newline)
        # in Contrib eintragen:
        self.add_item (newline[0], newline[1], newline[2])


    def save (self, newname=None):
        """ cueliste in Änderungsdatei oder newname speichern
        """
        if newname == None:
            self.file.backup()
            savename = os.path.join (Cue.CUEPATH, self.file.name())
        else:
            savename = os.path.join (Cue.CUEPATH, newname)+os.extsep+"csv"
        # print ("Savename: ", savename)
        
        with open (savename, 'w', newline='',encoding='utf-8') as cf:
            writer = csv.writer(cf) 
            # Header schreiben:
            writer.writerow (self._cuefields)
            # cuelist schreiben:
            rows = len (self._cuelist)
            fields = len (self._cuefields)
            for z in range(rows): # Zeile
                row = []
                for k in range (fields): #Feld
                    row.append (self._cuelist[z][k])
                # print (row)
                writer.writerow (row)


    def verify (self) -> bool:
        """ Cue File prüfen

        Fehler mit print dokumentieren, level in _cuelist korrigieren
        ok: True, Fehler: False
        """
        ret = True
        headlist = self.patch.headlist()
        for row in self._cuelist:
            # HeadNr:
            if row[0] not in headlist:
                print ("Head {}: nicht im Patch".format (row[0]))
                ret = False
            # Attr:
            if row[1] not in self.patch.attriblist(row[0]):
                print ("Head {}: Attribut {} nicht vorhanden".format (row[0], row[1]))
                ret = False
            # Level:
            if not len (row[2]): # leeres Feld
                row[2] = 0
            if isinstance (row[2], str): #str ->int
                level = int (row[2])
            else:
                level = row[2]
            if level < 0:
                row[2] = 0
                print ("Head {}: Level auf 0 gesetzt".format (row[0]))
                ret = False
            elif level > 255:
                print ("Head {}: Level auf 255 gesetzt".format (row[0]))
                row[2] = 255
                ret = False
        return ret
            
                
# --- Mix Methoden: -----------------------------------------------------   
    def add_item (self, head:str, attrib:str, level:str):
        """ eine Cue-Zeile in contrib einfügen 

        - index    = self.count
        - key      = Headnr-Attrib 
        - level    = Attribut-Level
        - attype   = Attributtyp 
        - in Cue.contrib eintragen: (self.count, key, attlevel, attype )
        """
        key = head + '-' + attrib
        attype = self.patch.attribtype (head, attrib)
        if not attype:
            attype = "unbekannt" # Patch und Cue vertragen sich nicht
        Cue.contrib.add (self.count, key, level, attype)
        self._active = True


    def cuelist_to_contrib (self):
        """ cuelist an contrib schicken
        """
        for row in self._cuelist:
            self.add_item (row[0], row[1], row[2])


    def rem_cuemix (self):
        """ Cueinfo aus contrib entfernen
        """
        tm = time.time ()
        Cue.contrib.add (self.count, "faderlevel", 0.0, tm)
        Cue.contrib.remove_index (self.count)
        self._active = False


    def mixoutput (self, head_attr, val):
        """ Mix Output Funktion

        den in contrib ermittelten Wert (HTP/LTP) für das Attribut setzen
        """
        if not self.contrib.paused:
            head,attr = head_attr.split(sep='-')
            self.patch.set_attribute (head, attr, val)
        # print ("mix:", head, attr, val)


# --- Attribut Methoden: -----------------------------------------------------
# nicht in Verwendung!!
    def set_attribute (self, head:str, attr:str, level:str):
        """ ["head","attr","level"] in _cuelist anhängen oder level ändern
        """
        # prüfen, ob head,attrib bereits in _cuelist:
        hindex = self._cuefields.index("HeadNr") # 0
        aindex = self._cuefields.index("Attr")   # 1
        lindex = self._cuefields.index("Level")  # 2
        rows = len (self._cuelist)
        found = 0
        for z in range(rows):   # Zeile
            if (head == self._cuelist[z][hindex]) and \
                (attr == self._cuelist[z][aindex]):
                found = 1
                self._cuelist[z][lindex] = level # level geändert
        if not found:
            self._cuelist.append ([head,attr,level])
        # print (self._cuelist)


    def remove_attribute (self, head, attr):
        """ ["head","attr", ...] aus _cuelist entfernen
        """
        # head,attrib in _cuelist suchen:
        hindex = self._cuefields.index("HeadNr") # 0
        aindex = self._cuefields.index("Attr")   # 1
        rows = len (self._cuelist)
        found = -1
        for z in range(rows):   # Zeile
            if (head == self._cuelist[z][hindex]) and \
                (attr == self._cuelist[z][aindex]):
                found = z
        if found != -1:
            rem = self._cuelist.pop (found)
            print (rem)
        # print (self._cuelist)


# ------------------------------------------------------------------------------
# Level ändern:

    def __set_level (self, newlevel):
        self._level = newlevel
        if newlevel == 0: # automatisches Update und self.rem_cuemix
            if self._autoupdate:
                self.get_cuelist()
                self._autoupdate = False
            if self._active:
                self.rem_cuemix ()
        else:
            tm = time.time()
            Cue.contrib.add (self.count, "faderlevel", self._level, tm)
            if not self._autoupdate:
                self._autoupdate = True
            if not self._active:
                self.cuelist_to_contrib ()


    def __get_level (self):
        return self._level

    level = property(__get_level, __set_level)


# ------------------------------------------------------------------------------
# Unit Test:  
# siehe "test cue.py"
