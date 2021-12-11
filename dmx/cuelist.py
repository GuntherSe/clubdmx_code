#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
class Cuelist

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

"""

import time
import os
import os.path
import threading
import csv

from csvfileclass import Csvfile

from patch import Patch
from ola import OscOla
from cue import Cue



class Cuelist ():

    instances = []
    timeout = 0.02 # 0.02
    running = False
    CUELISTPATH = ""
    init_done = 0
    
    def __init__ (self, patch):
        self.__class__.instances.append (self)
        if Cuelist.init_done == 0:
            if Cuelist.CUELISTPATH == "":
                path = os.path.dirname(os.path.realpath(__file__))
                self.set_path (path)

        self.patch = patch
        fname = os.path.join (Cuelist.CUELISTPATH, "_neu")
        self.file = Csvfile (fname) 
        self.filetime = 0.0 # bei get_cuelist aktualisieren
        self._autoupdate = False # update, wenn _level == 0
        self._listfields = [] # Feldnamen der cuelist
        self._idlist = [] # liste der in der cuelist vorhandenen Id's, sortiert
                          # diese Id's sind vom Typ float

        self.cuelist = {} # Dict, das die Cue-Informationen enthält
        self.outcue = Cue (patch) # dieser content wird an contrib geschickt
        self.outcue.level = 1.0
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

        if not Cuelist.running:
            Cuelist.running = True
            Cuelist.fade_thread = threading.Thread (target=Cuelist.run)
            Cuelist.fade_thread.setDaemon (True)
            if not os.environ.get ("PYTHONANYWHERE") == "true":
                Cuelist.fade_thread.start ()

    def __repr__(self):
        return '<Cuelist {}>'.format(self.file.shortname())  

    @classmethod
    def printInstances (cls):
        for instance in cls.instances:
            print (instance)

    @classmethod
    def set_path (cls, newpath):
        """ Pfad für Cuelisten-Verzeichnis festlegen 
        
        newpath: 'Raum-Verzeichnis', Absolut-Pfad
        """
        Cuelist.CUELISTPATH = os.path.join (newpath, "cuelist")


    @classmethod 
    def run (cls):
        """ Kalkulations-loop """
        while True:
            cls.calc_all_cuelists ()
            time.sleep (cls.timeout)

    @classmethod
    def calc_all_cuelists (cls):
        """ alle Faderlevel berechnen 
        """
        tm = time.time ()
        try:
            for instance in cls.instances:
                instance.calc_cuecontent (tm)
        except: # instances-Liste kann neu erzeugt werden
            pass


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
        if 0 <= pos < len (self.cuelist):
            id = self._idlist[pos]
            ret = self.cuelist[id]
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


    def tmfactor (self, id:float, tm:"time", direction:str) -> dict:
        """ Fadefaktor berechnen
        
        id: ID des Cues
        tm: aktuelle Zeit
        direction: 'in' oder 'out'
        return: {in:float zw. 0 und 1, out: Float zw. 0 und 1}
        """
        infactor = 0.0 # default
        outfactor = 1.0 # default 
        xfade = True # default

        if id in self._idlist:
            if direction == "in":
            # Zeitfaktor für fade-in:
                waitintm = self.cuelist[id]["Waitin"]
                fadeintm = self.cuelist[id]["Fadein"]
                if tm <  self.start_tm + waitintm: # in der Wartezeit
                    infactor = 0.0
                else:
                    if fadeintm > 0:
                        x = (tm - (self.start_tm + waitintm)) / fadeintm
                        if x < 0: # kann beim startup/Einlesen vorkommen
                            x = 0.0
                        infactor = min (1.0, x)
                    else:
                        infactor = 1.0

            elif direction == "out":
            # Zeitfaktor für Fade-out:
                waitouttm = self.cuelist[id]["Waitout"]
                fadeouttm = self.cuelist[id]["Fadeout"]
                if fadeouttm != -1.0: # crossfade
                    xfade = False

                if tm < self.start_tm + waitouttm:
                    outfactor = 1.0
                else:
                    if fadeouttm > 0:
                        x = (tm - (self.start_tm + waitouttm)) / fadeouttm
                        if x < 0: 
                            x = 0.0
                        outfactor = max (0.0, 1-x)
                    else:
                        outfactor = 0.0

            # Verbleibende Zeit:
            # total_tm = max (waitintm+fadeintm, waitouttm+fadeouttm)
            # self.remain_tm = self.start_tm + total_tm - tm
        return {"in":infactor, "out":outfactor, "xfade":xfade}

        # else:
        #     # self.remain_tm = 0.0
        #     return {"in":0.0, "out":1.0, "xfade":False}

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


    def calc_cuecontent (self, tm:"time"):
        """ aktuellen Content berechnen 

        outcue._cuecontent berechnen, wird permanent durchgeführt, siehe self.run()
        tm = aktuelle Zeit 
        hängt ab von: start_tm, tm, currentcue, nextcue

        """
        if self.is_paused or self.level == 0: # Pause - keine Auswertung
            self.update_cuelist ()
            return

        curfactor = self.tmfactor (self.currentid, tm, "out")
        nextfactor = self.tmfactor (self.nextid, tm, "in")

        # self.fadein_percent = int (nextfactor["in"] * 100)
        # if curfactor["xfade"]:
        #     self.fadeout_percent = 100 - self.fadein_percent
        # else:
        #     self.fadeout_percent = int (curfactor["out"] * 100)

        # Übergänge berechnen:
        # 1. items, die in nextcue vorkommen:
        if self.is_fading_in:
            self.fadein_percent = int (nextfactor["in"] * 100)
            for item in self.nextcue.cuecontent ():
                itemkey = item[0] + item[1]
                nextlevel = int (item[2])
                if itemkey in self.currentkeys: # kommt auch in currentcue vor
                    # Crossfade
                    index = self.currentkeys.index (itemkey)
                    curlevel = int (self.currentlevels[index])
                    level = curlevel + nextfactor["in"] * (nextlevel - curlevel)
                else:
                    # Fade in 
                    level = nextfactor["in"] * nextlevel
                self.outcue.line_to_cuecontent ([item[0],item[1],
                    str(int(level))])
                # print (f"Fading in: {item[0]} {item[1]} {int(level)}")
        
        # 2. items, die nur in currentcue vorkommen:
        if curfactor["xfade"] == True: # crossfade
            self.is_fading_out = self.is_fading_in
            curfactor["out"] = 1 - nextfactor["in"]

        if self.is_fading_out: # and not (itemkey in self.nextkeys):
            self.fadeout_percent = int (curfactor["out"] * 100)
            for item in self.currentcue.cuecontent ():
                itemkey = item[0] + item[1]
                if itemkey not in self.nextkeys:
                    level = curfactor["out"] * int (item[2])
                    self.outcue.line_to_cuecontent ([item[0],item[1],
                        str(int(level))])
                    # print (f"Fading out: {item[0]} {item[1]} {int(level)}")

        #Test:
        # print (f"\rxFade: {self.fadein_percent} {self.fadeout_percent}", end='')
        # current Cue und next Cue evtl updaten:
        if self.is_fading_in and nextfactor["in"] == 1:
            self.is_fading_in = False
        if self.is_fading_out and curfactor["out"] == 0:
            self.is_fading_out = False
        fading_done = (not self.is_fading_in) and (not self.is_fading_out)

        if fading_done and not self.is_loaded: # and not self.currentpos == -1:
            self.is_loaded = True
            # print ("\rFading Done.\nCMD: ", end='')

            self.fadeout_percent = 100
            self.fadein_percent = 0

            self.update_cuelist ()

            # nextcue wird zum currentcue, neuen nextcue einlesen
            self.currentpos = self.nextpos
            self.setcurrentcue (self.currentpos)
            self.current_to_output () # outcue mit currentcue abgleichen
            if self.nextprep == self.nextpos:
                self.increment_nextprep () # nextprep um 1 erhöhen
            # else: nextprep wurde bereits verändert

            # Stay Time:
            staytm = self.cuelist[self.currentid]["Stay"]
            if staytm == -1:
                self.go_time = -1
            else:
                self.go_time = tm + staytm
            
        # Stay-Time abgelaufen:
        if (self.go_time != -1) and (tm > self.go_time):
            self.go_time = -1
            self.go ()


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

    def go (self, cuenr:str=""):
        """ Fade beginnen und Startzeit speichern 

        cuenr: nächste Cuenr oder '-1' -> go back
        """
        if self.is_fading_in: # aktueller Fade noch nicht abgeschlossen
            # print ("GO between...")
            self.output_to_current ()

        # nextpos bestimmen:
        if cuenr == "":
            if not self.is_paused:
                self.nextpos = self.nextprep
                # self.increment_nextpos ()
                # bei GO nach Pause bleibt nextpos gleich
        elif cuenr == "-1": # go back
            if self.is_paused:
                # self.nextpos = self.currentpos
                self.nextprep = self.currentpos
                # self.setnextcue (self.nextpos)
            else:
                self.decrement_nextprep ()
        else: # nächste cuenr angegeben
            try:
                id = float (cuenr) # evtl Error
                pos = self._idlist.index (id) # evtl ValueError
                self.nextprep = pos # cuenr vorhanden
            except: # cuenr nicht vorhanden: stehen bleiben
                self.nextprep = self.currentpos

        if self.is_paused:
            self.start_tm = time.time () - self.elapsed_tm
            self.is_paused = False
            # alle anderen Statuswerte bleiben gleich
            return

        self.setnextcue (self.nextprep) 
        if self.nextpos != self.currentpos:
            self.is_fading_in = True
            self.is_fading_out = True
            self.is_loaded = False
            self.start_tm = time.time ()


    def pause (self):
        """ Zeitfunktionen (Fade, Stay) pausieren
        """
        if not self.is_paused:
            self.is_paused = True
            self.elapsed_tm = time.time () - self.start_tm


    def output_to_current (self):
        """output Cue wird current Cue, wenn GO während fading_in 
        getriggert wird
        """
        # output Cue kopieren:
        for item in self.outcue.cuecontent ():
            # item kommt von current Cue
            # oder item kommt von next Cue
            self.currentcue.line_to_cuecontent (item)

        # currentkeys updaten:
        for item in self.currentcue.cuecontent ():
            key = item[0]+item[1]
            if key not in self.currentkeys:
                self.currentkeys.append (key) 
                self.currentlevels.append (item[2])


    def current_to_output (self):
        """ current Cue an out Cue kopieren
        
        Nach dem Fade ausführen, um überzählige Null-Items zu entfernen
        current keys und levels neu erzeugen
        """
        self.outcue.content[:] = [item for item in self.outcue.content \
            if item[0]+item[1] in self.currentkeys]


# File Methoden: --------------------------------------------------------------
    def open (self, fname = ""):
        """ öffnet fname und liest cuelist ein 

        wenn fname == '', dann cuelist neu einlesen
        """
        if fname:
            openname = os.path.join (Cuelist.CUELISTPATH, fname)
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
            self.cuelist = {} # cuelist leeren
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
                        self.cuelist[num] = row
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
            fname = self.cuelist[self.currentid]["Filename"]
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
            fname = self.cuelist[self.nextid]["Filename"]
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
        self.currentpos = -1
        self.currentid = 0.0 
        fname = "_neu"
        self.currentcue.open (fname)
        # next Cue:
        if len (self.cuelist) == 0:
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
        strval = self.cuelist[row][col]
        if strval == "":
            if empty_allowed: 
                self.cuelist[row][col] = -1.0
            else:
                self.cuelist[row][col] = 0.0    
        else:
            try:
                val = float (strval)
                if val < 0: # fehlerhafte csv-Datei
                    val = 0.0
            except:
                val = 0.0
            self.cuelist[row][col] = val


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
    Cuelist.set_path (os.getcwd())

    list1 = Cuelist (patch)
    list1.open ("list1")

    pp = pprint.PrettyPrinter(depth=6)


    infotxt = """
    ---- Cuelist Test -----

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
            g <Nr> = GO zu Cue <Nr>
            b = GO back
            p = Pause 

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
                pp.pprint (list1.cuelist)
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
            elif i == 'g':
                if len (inp) > 1:
                    list1.go (inp[1])
                else:
                    list1.go ()
                print (f"{list1.currentid} -> {list1.nextid}")
            elif i == 'b':
                list1.go ("-1")
                print (f"back: {list1.currentid} -> {list1.nextid}")
            elif i == 'p':
                list1.pause ()
                print ("Pause. Weiter mit g oder b.")
            else:
                pass
    finally:
        print ("bye...")

