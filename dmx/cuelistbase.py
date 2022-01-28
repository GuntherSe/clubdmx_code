#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
class Cuelistbase

Cuelist ist eine Tabelle mit folgender Struktur:
Id,Cue,Fadein,Fadeout,Waitin,Waitout,Text,Comment
Id: Laufende Nummer mit evtl 2 Kommastellen, z.B 1, 1.2, 1.23
Cue: Filename, lokalisiert in <room>/cue
Fadein, Fadeout, Waitin, Waitout: Zeiten in sec
Stay: '' .. Warten auf GO, Zeit >= 0 in sec .. Wartezeit vor Auto-GO
Text: Anzeigetext kurz
Comment: Anzeigetext lang = Cue-Information

Eine Cuelist wird durch den outcue in Cue.contrib in den Mix eingebunden. 
Im Gegensatz zum Cue, wo der 
Cue-Content in einem File gelistet und daher statisch ist, ist der in den 
Mix eingebundene Content dynamisch: Abhängig von aktuellem und nächsten 
Cue und dem Zeitpunkt wird der _cuecontent von outcue berechnet.

Cuelistbase ist der Teil der Cuelist, ohne die dynamische Berechnung, also
das Grundgerüst

"""

import time
import os
import os.path
# import threading
import csv

from csvfileclass import Csvfile

from patch import Patch
from ola import OscOla
from cue import Cue



class Cuelistbase ():

    instances = []
    timeout = 0.02 # 0.02
    running = False
    CUELISTPATH = ""
    init_done = 0
    
    def __init__ (self, patch):
        self.__class__.instances.append (self)
        if Cuelistbase.init_done == 0:
            if Cuelistbase.CUELISTPATH == "":
                path = os.path.dirname(os.path.realpath(__file__))
                self.set_path (path)

        self.patch = patch
        fname = os.path.join (Cuelistbase.CUELISTPATH, "_neu")
        self.file = Csvfile (fname) 
        self.filetime = 0.0 # bei get_cuelist aktualisieren
        self._autoupdate = False # update, wenn _level == 0
        self._listfields = [] # Feldnamen der cuelist
        self._idlist = [] # liste der in der cuelist vorhandenen Id's, sortiert
                          # diese Id's sind vom Typ float

        self.cuedict = {} # Dict, das die Cue-Informationen enthält
        self.outcue = Cue (patch) # dieser content wird an contrib geschickt
        self.outcue.level = 0.0
        self.location = "pages"
        # self.text = ""
        # current-Werte:
        self.currentcue = Cue (patch) # Infos zum aktuellen Cue
        self.currentid = 0.0 # float
        self.currentpos = 0 # Position des current Cue in self._idlist
        self.currentkeys = [] # Liste an keys = 'Headnr'+'Attrib'
        self.currentlevels = [] # Liste an Levels zu den Keys
        # next-Werte:
        self.nextcue = Cue (patch) # Infos zum nächsten Cue
        self.nextid = 0.0 # float
        self.nextpos = 0 # Position des next Cue in self._idlist
        self.nextkeys = []
        self.nextprep = 0   # Nächste Position in Vorbereitung, 
                            # nextpos wird erst bei go festgelegt
        # Status:
        self.is_fading_in = True
        self.is_fading_out = False
        self.fadein_percent = 0
        self.fadeout_percent = 100
        self.is_loaded = False  # True: keine Fades, currentcue am output
        self.is_paused = False # True: Zeitfunktionen (Fade, Stay) pausieren
        self.elapsed_tm = 0.0 # vergangene Zeit beim Drücken von Pause
        self.start_tm = time.time ()
        self.go_time = -1 # Zeit für Go nach Stay-Time


    def __repr__(self):
        return '<Cuelistbase {}>'.format(self.file.shortname())  

    @classmethod
    def printInstances (cls):
        for instance in cls.instances:
            print (instance)

    @classmethod
    def set_path (cls, newpath):
        """ Pfad für Cuelisten-Verzeichnis festlegen 
        
        newpath: 'Raum-Verzeichnis', Absolut-Pfad
        """
        Cuelistbase.CUELISTPATH = os.path.join (newpath, "cuelist")


    @classmethod
    def items (cls) ->list:
        """ alle cuelists in dictlist ausgeben
        """
        ret = []
        for inst in cls.instances:
            item = {}
            item["Text"] = inst.outcue.text
            item["Filename"] = inst.file.shortname()
            item["Index"] = cls.instances.index (inst)
            # Status:
            # item["current_id"] = str (cls.currentid)
            ret.append (item)
        return ret
    

    def line (self, pos:int) -> dict:
        """ liefert cuelist[pos] als dict 
        """
        ret = {}
        if 0 <= pos < len (self.cuedict):
            id = self._idlist[pos]
            ret = self.cuedict[id]
        return ret

    def status (self) -> dict:
        """ aktueller Status der Cuelist"""
        ret = {}
        # current-Werte:
        ret["currentline"] = self.line (self.currentpos)
        if "Id" in ret["currentline"]:
            numstr = ret["currentline"]["Id"].replace ('.', '-')
        else:
            numstr = ''
        ret["currentid"] = numstr # String mit Umwandlung von '.' in '-'
        ret["nextline"] = self.line (self.nextprep)
        if "Id" in ret["nextline"]:
            numstr = ret["nextline"]["Id"].replace ('.', '-')
        else:
            numstr = ''
        ret["nextid"] = numstr
        # Status:
        ret["fading_in"] = self.fadein_percent
        ret["fading_out"] = self.fadeout_percent
        ret["is_paused"] = "true" if self.is_paused else "false" # True: Zeitfunktionen (Fade, Stay) pausieren
        ret["self.elapsed_tm"] = self.elapsed_tm # vergangene Zeit beim Drücken von Pause
        ret["start_tm"] = self.start_tm 
        # ret["go_time"] = self.go_time # Zeit für Go nach Stay-Time
        return ret


    def update_cuelist (self):
        """ cueliste updaten 
        wenn Fades abgeschlossen sind
        wenn pause
        wenn level == 0
        """
        # evtl. könnte next ID gelöscht sein
        nextid = self.nextid
        self.get_cuelist (reset_ids=False)
        if not (nextid in self._idlist):
            self.nextpos = 0
            self.reset_ids ()


    def increment_nextprep (self):
        """ nextprep um 1 erhöhen oder zu 0 springen
        nextpos wird erst bei GO aktualisiert
        """
        if self.nextprep < len (self._idlist) -1:
            self.nextprep += 1
        else:
            self.nextprep = 0 # beginnt von vorn


    def decrement_nextprep (self):
        """ nextprep um 1 vermindern oder zum Ende der cuelist springen
        nextpos wird erst bei GO aktualisiert
        """
        if self.nextprep > 0:
            self.nextprep -= 1
        else: # zum Ende springen
            self.nextprep = len (self._idlist) -1

# File Methoden: --------------------------------------------------------------
    def open (self, fname = ""):
        """ öffnet fname und liest cuelist ein 

        wenn fname == '', dann cuelist neu einlesen
        """
        if fname:
            openname = os.path.join (Cuelistbase.CUELISTPATH, fname)
            self.file.name (openname)
        self.get_cuelist ()

        # ersten Cue starten:
        self.is_fading_in = True
        # self.is_loaded = True
        self.start_tm = time.time ()
        # self.go ()


    def get_cuelist (self, reset_ids = True) ->int:
        """ Cueliste einlesen

        Struktur: {'1':{'Id':'1','Cue':'cue1','Fadein':'fade1', ...}
                   '1.10':{'Id':'1.10','Cue':'cue2', ...}
                   ...}
        """
        filename = self.file.name ()
        if os.path.isfile (filename) and \
            os.path.getmtime(filename) > self.filetime:
            self.cuedict = {} # cuelist leeren
            self._idlist = []
            with open (filename, 'r',encoding='utf-8') as pf: # zum Lesen öffnen und einlesen
                reader = csv.DictReader (pf, restval= '')
                self._listfields = reader.fieldnames
                if "Id" not in self._listfields:
                    # muss vor Einlesen geprüft werden
                    print ("Feld 'Id' nicht in Cueliste gefunden")
                    return

                for row in reader:
                    try: # kann in float konvertiert werden:
                        num = float (row["Id"])
                        self.cuedict[num] = row
                        self._idlist.append (num)
                    except:
                        print (f"{row['Id']} ist keine Dezimalzahl.")

            self._idlist = sorted (self._idlist)
            self.verify()
            if reset_ids:
                self.reset_ids ()
            self.filetime = os.path.getmtime (filename)
        else:
            pass


    def setcurrentcue (self, pos):
        """ Infos zu currentcue ermitteln 
        zuerst currentid, dann die Infos dazu ermitteln
        """
        if 0 <= pos < len (self._idlist):
            self.currentid    = self._idlist[pos]
            fname = self.cuedict[self.currentid]["Filename"]
            self.currentcue.open (fname)
            self.currentkeys.clear ()
            self.currentlevels.clear ()
            for item in self.currentcue.cuecontent ():
                self.currentkeys.append (item[0]+item[1]) # head-attrib ohne Bindestrich
                self.currentlevels.append (item[2])
        # print ("Currentkeys: ", self.currentkeys)


    def setnextcue (self, pos):
        """ Infos zu nextcue ermitteln 
        zuerst nextid, dann die Infos dazu ermitteln
        """
        if 0 <= pos < len (self._idlist):
            self.nextpos = pos
            self.nextid    = self._idlist[pos]
            fname = self.cuedict[self.nextid]["Filename"]
            self.nextcue.open (fname)
            self.nextkeys.clear ()
            for item in self.nextcue.cuecontent ():
                self.nextkeys.append (item[0]+item[1]) # head-attrib ohne Bindestrich
        # print ("Nextkeys: ", self.nextkeys)

    def verify (self):
        """ Cueliste prüfen 
        """
        ret = True
        # Feldnamen prüfen:
        required = ["Id", "Filename", "Fadein", "Fadeout", "Waitin", "Waitout", \
            "Stay", "Text", "Comment"]
        for fieldname in required:
            if fieldname not in self._listfields:
                print (f"Feld '{fieldname}' nicht gefunden. ")
                ret = False

        # Zeitwerte prüfen und in float wandeln:
        timecols = ["Fadein", "Waitin", "Waitout"]
        specialtimes = ["Fadeout", "Stay"] # können leer sein
        for row in self._idlist:
            for col in timecols:
                self.check_tm_value (row, col)
            for col in specialtimes:
                self.check_tm_value (row, col, empty_allowed=True)
        return ret


    def reset_ids (self):
        """ current Cue und next Cue auf Ausgangswerte setzen
        Damit wird beim __init__ ein Einfaden des ersten Cues ausgelöst.
        """
        # current Cue:
        self.currentpos = 0 #-1
        self.currentid = 0.0 
        fname = "_neu"
        self.currentcue.open (fname)
        # next Cue:
        if len (self.cuedict) == 0:
            self.nextid = 0.0 #"-1"
            fname = "_neu"
            self.nextcue.open (fname)
        else: 
            self.setnextcue (0)
            self.nextprep = 0


    def check_tm_value (self, row:float, col:str, empty_allowed=False):
        """ Zeitangabe in cuelist prüfen
        
        empty_allowed: True für Fadeout und Stay.
        Fadeout: -> crossfade
        Stay: -> warten auf Go
        keine negativen Werte, str als float umrechenbar
        """
        strval = self.cuedict[row][col]
        if isinstance (strval, str):
            strval = strval.strip ()
        if strval == "":
            if empty_allowed: 
                self.cuedict[row][col] = -1.0
            else:
                self.cuedict[row][col] = 0.0    
        else:
            try:
                val = float (strval)
                if val < 0: # fehlerhafte csv-Datei
                    val = 0.0
            except:
                val = 0.0
            self.cuedict[row][col] = val


# --- Level Property: -----------------------------------------------------
    def __set_level (self, newlevel):
        self.outcue.level = newlevel

    def __get_level (self):
        return self.outcue.level

    level = property(__get_level, __set_level)

# --- Text Property: -------------------------------------------------------
    def __set_text (self, newtext):
        self.outcue.text = newtext

    def __get_text (self):
        return self.outcue.text

    text = property(__get_text, __set_text)

# --- id Property: ----------------------------------------------------------
    def __set_id (self, newid):
        self.outcue.id = newid

    def __get_id (self):
        return self.outcue.id

    id = property(__get_id, __set_id)

# --- midioutput Property: ---------------------------------------------------
    def __set_midioutput (self, newval):
        self.outcue.midioutput = newval

    def __get_midioutput (self):
        return self.outcue.midioutput

    midioutput = property(__get_midioutput, __set_midioutput)

# --- midicontroller Property: ----------------------------------------------
    def __set_midictl (self, newval):
        self.outcue.midicontroller = newval

    def __get_midictl (self):
        return self.outcue.midicontroller

    midicontroller = property(__get_midictl, __set_midictl)


# --- Test -----------------------------------------------------------------
if __name__ == "__main__":
    """ Test Cuelist:
    """
    import pprint # pretty print


    os.chdir ("C:\\Users\\Gunther\\OneDrive\\Programmierung\\clubdmx_rooms\\test")
    print ("ich bin hier: ", os.getcwd())
    patch = Patch()
    patch.set_path (os.getcwd())
    patch.open ("LED stripe2")

    ola   = OscOla ()
    ola.set_ola_ip ("192.168.0.11")
    print("Verbinde zu OLA-device: {0}".format (ola.ola_ip))
    ola.start_mixing()

    patch.set_universes (2)
    Cue.set_path (os.getcwd())
    Cuelistbase.set_path (os.getcwd())

    list1 = Cuelistbase (patch)
    list1.open ("list1")
    list1.level = 1.0

    pp = pprint.PrettyPrinter(depth=6)


    infotxt = """
    ---- Cuelistbase Test -----

    Kommandos: x = Exit
            # = zeige diese Info 
            c = Zeige Cuelist 1
            i = Zeige OutCue
            d = zeige Patch Dict
            m = Zeige Mix Universum 1
            s = Status

            1 = zeige current Cue Info
            2 = zeige current Cue content
            3 = zeige nächste Cue Info
            + = nächster Cue um 1 höher
            - = nächster Cue um 1 niedriger
    """

    print (infotxt)
    try:
        i = 1
        while i != 'x':
            txt = input ("CMD: ")
            inp = txt.split () # input list
            if inp != []:
                i = inp[0]
            else:
                i = "ENTER"
            if i == '#':
                print (infotxt)
            elif i == 'c':
                pp.pprint (list1.cuedict)
            elif i == 'm':
                uni = 1 # input ("Universum: ")
                print (patch.show_mix(uni))
            elif i == 'd':
                print (patch.pdict)
            elif i == 'i':
                print (list1.outcue.cuecontent())
            elif i == 's':
                pp.pprint (list1.status ())
            elif i == '1':
                try:
                    print (f"current id:{list1.currentid}, ", end='')
                    print (f"pos:{list1.currentpos}, {list1.currentcue}" )
                except:
                    pass
            elif i == '2':
                pp.pprint (list1.currentcue.cuecontent())    
            elif i == '3':
                print (f"nächste Pos: {list1.nextprep}")
            elif i == '+':
                list1.increment_nextprep ()
                print (f"nächste Pos: {list1.nextprep}")
            elif i == '-':
                list1.decrement_nextprep ()
                print (f"nächste Pos: {list1.nextprep}")
            else:
                pass
    finally:
        print ("bye...")

