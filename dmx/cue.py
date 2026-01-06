#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" class Cue
Ein Cue ist eine Sammlung von Attributwerten diverser Heads.
Wird ein Cue ausgeführt (cuecontent_to_contrib), werden die Werte an
den Mixer geschickt.

Für alle Attribute wird ein dict geführt: content

      
"""

from asyncio.log import logger
import os
import os.path
import time
import csv

from contribclass import Contrib
from csvfileclass import Csvfile

import logging
from loggingbase import Logbase

class Cue ():
    # global: 
    CUEPATH = ""
    contrib = Contrib()
    init_done = 0
    
    # ein logger für alle Cue-Instanzen:
    baselogger = Logbase ()
    logger = logging.getLogger (__name__)
    file_handler = baselogger.filehandler ("cue.log")
    logger.addHandler (file_handler)

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

        self.count = id (self) # eindeutige id für contrib-mix
        self.patch = patch
        self.content = [] # Struktur: [[Head1,Att1,Lev1], [Head2,Att2,Lev2], ...]
        self._cuefields = [] # ['HeadNr', 'Attr', 'Level']
        self._autoupdate = False # Auto-Update wenn _level == 0
        fname = os.path.join (Cue.CUEPATH, "_neu")
        self.file     = Csvfile (fname)   # Default Cue File Name
        self.filetime = 0.0  # bei get_cuecontent aktualisieren (os.path.getmtime)
        self._active  = False  # cue in Contrib eingetragen -> self._active = True
        self._level   = 1.0  # Wert in [0..1]
        self.level    = 0.0  # Zuweisung mit Properties und Eintrag in Contrib
        # zur späteren Verwendung in Fader und Buttons:
        self.text     = ""  # Anzeigetext
        self.location = ""  # in welcher Cue-Gruppe
                            # (cuebuttons, exebuttons1, exebuttons2, 
                            # cuefaders, exefaders)
        self.id       = ""  # = location + Zeilennummer (ab 0) in 
                            # CSV-Datei der Cue-Gruppe
                            # wird bei startup erzeugt
        self.midioutput = -1     # Midioutput, an den Status geschickt wird
        self.midicontroller = -1 # Midicontroller, an den Status geschickt wird
        

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

        fname: ohne Pfad und Endung
        Wenn anderer fname, dann ftime auf 0 setzen.
        """
        if fname:
            if fname != self.file.shortname ():
                self.filetime = 0.0
            openname = os.path.join(Cue.CUEPATH, fname)
            self.file.name (openname)
        # else: filename = "_neu"
        self.get_cuecontent()


    def get_cuecontent (self):
        """ File einlesen

        siehe Patch._get_pdict()
        """
        filename = self.file.name()
        # print ("Cuefile: ", filename)
        
        if os.path.isfile (filename) and \
            os.path.getmtime(filename) > self.filetime:
            self.rem_cuemix() # evtl aktiven Mix entfernen
            self.content.clear () # = []
            with open (filename, 'r',encoding='utf-8') as pf: # zum Lesen öffnen und einlesen
                reader = csv.DictReader (pf, restval= '')
                self._cuefields = reader.fieldnames
                if self._cuefields:
                    for row in reader:
                        attribs = [] # zugehörige Attribute
                        for item in self._cuefields:
                            attribs.append (row[item])
                        self.content.append (attribs)
                else:
                    logger.error ("cuefields nicht definiert.")
            self.verify()
            self.filetime = os.path.getmtime (filename)
        else:
            # kein File gefunden oder keine Änderungen
            pass


    def cuecontent (self):
        return self.content


    def to_dictlist (self):
        """ _cuecontent in dict-Notation

        Struktur: [{'HeadNr'='head-1','Attr'='att-1','Level'='level-1'},
                   {'HeadNr'='head-2','Attr'='att-2','Level'='level-2'},
                    ... ]
        """
        ret = []
        if not self._cuefields:
            return ret
        for line in self.content:
            retline = {}
            for i in range (len (line)):
                retline[self._cuefields[i]] = line[i] 
            ret.append (retline)
        return ret


    def line_to_cuecontent (self, newline:list):
        """ line in _cuecontent integrieren 

        entweder update oder append
        """
        found = 0
        for line in self.content:
            if line[0] == newline [0] and line[1] == newline [1]:
                found = 1
                line[2] = newline[2]
        if not found:
            self.content.append (newline)
        # in Contrib eintragen:
        self.add_item (newline[0], newline[1], newline[2])


    def save (self, newname=None):
        """ cuecontent in Änderungsdatei oder newname speichern
        """
        if newname == None:
            self.file.backup()
            savename = os.path.join (Cue.CUEPATH, self.file.name())
        else:
            savename = os.path.join (Cue.CUEPATH, newname)+os.extsep+"csv"
        # print ("Savename: ", savename)
        if self._cuefields:
            with open (savename, 'w', newline='',encoding='utf-8') as cf:
                writer = csv.writer(cf) 
                # Header schreiben:
                writer.writerow (self._cuefields)
                # cuecontent schreiben:
                rows = len (self.content)
                fields = len (self._cuefields)
                for z in range(rows): # Zeile
                    row = []
                    for k in range (fields): #Feld
                        row.append (self.content[z][k])
                    # print (row)
                    writer.writerow (row)
        else:
            logger.error ("Cuefields nicht definiert!")

    def verify (self) -> bool:
        """ Cue File prüfen

        Fehler mit print dokumentieren, level in _cuecontent korrigieren
        ok: True, Fehler: False
        """
        ret = True
        headlist = self.patch.headlist()
        cuename = self.file.shortname ()
        for row in self.content:
            # HeadNr:
            if row[0] not in headlist:
                # msg = "Head {}: nicht im Patch".format (row[0])
                self.logger.warning (f"Cue {cuename}: Head {row[0]} nicht im Patch.")
                ret = False
            # Attr:
            if row[1] not in self.patch.attriblist(row[0]):
                msg = f"Cue {cuename}: Attribut {row[1]} für Head {row[0]}" + \
                      " ist nicht vorhanden"
                self.logger.warning (msg)
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
                self.logger.warning (f"{cuename}: Head {row[0]} Level auf 0 gesetzt")
                ret = False
            elif level > 255:
                self.logger.warning (f"{cuename}: Head {row[0]} Level auf 255 gesetzt")
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


    def cuecontent_to_contrib (self):
        """ cuecontent an contrib schicken
        """
        for row in self.content:
            self.add_item (row[0], row[1], row[2])


    def rem_cuemix (self):
        """ Cueinfo aus contrib entfernen
        """
        tm = time.time ()
        Cue.contrib.add (self.count, "faderlevel", 0.0, tm)
        Cue.contrib.remove_index (self.count)
        self._active = False


    def mixoutput (self, head, attr, val):
        """ Mix Output Funktion

        den in contrib ermittelten Wert (HTP/LTP) für das Attribut setzen
        für jedes Attribut in jedem Head genau 1 Wert (nicht mehrmals aufrufen)
        wird nur bei Änderungen aufgerufen
        """
        if not self.contrib.paused:
            self.patch.set_attribute (head, attr, val)
        # print ("mix:", head, attr, val)


# --- Attribut Methoden: -----------------------------------------------------
    def set_attribute (self, head:str, attr:str, level:str):
        """ ["head","attr","level"] in _cuecontent anhängen oder level ändern
        """
        # prüfen, ob head,attrib bereits in _cuecontent:
        if self._cuefields:
            hindex = self._cuefields.index("HeadNr") # 0
            aindex = self._cuefields.index("Attr")   # 1
            lindex = self._cuefields.index("Level")  # 2
            rows = len (self.content)
            found = 0
            for z in range(rows):   # Zeile
                if (head == self.content[z][hindex]) and \
                    (attr == self.content[z][aindex]):
                    found = 1
                    self.content[z][lindex] = level # level geändert
            if not found:
                self.content.append ([head,attr,level])
        else:
            logger.error ("Cuefields nicht definiert!")
        # print (self.content)


    def remove_attribute (self, head, attr):
        """ ["head","attr", ...] aus _cuecontent entfernen
        """
        # head,attrib in _cuecontent suchen:
        if self._cuefields:
            hindex = self._cuefields.index("HeadNr") # 0
            aindex = self._cuefields.index("Attr")   # 1
            rows = len (self.content)
            found = -1
            for z in range(rows):   # Zeile
                if (head == self.content[z][hindex]) and \
                    (attr == self.content[z][aindex]):
                    found = z
            if found != -1:
                rem = self.content.pop (found)
                self.logger.debug (rem)
        else:
            logger.error ("Cuefields nicht definiert!")
        # print (self.content)


    def has_key (self, head:str, attrib:str) ->str:
        """ prüfen, ob key in Cue enthalten ist

        key: headnr-attrib
        return: level, wenn key gefunden, sonst 0
        """
        # head, attrib = key.split (sep='-')
        for row in self.content:
            if row[0] == head and row[1] == attrib:
                return row[2]
        return ""

# ------------------------------------------------------------------------------
# Level ändern:

    def __set_level (self, newlevel):
        self._level = newlevel
        if newlevel == 0: # automatisches Update und self.rem_cuemix
            if self._autoupdate:
                self.get_cuecontent()
                self._autoupdate = False
            if self._active:
                self.rem_cuemix ()
        else:
            tm = time.time()
            Cue.contrib.add (self.count, "faderlevel", self._level, tm)
            if not self._autoupdate:
                self._autoupdate = True
            if not self._active:
                self.cuecontent_to_contrib ()


    def __get_level (self):
        return self._level

    level = property(__get_level, __set_level)


# ------------------------------------------------------------------------------
# Unit Test:  
# siehe "test cue.py"
