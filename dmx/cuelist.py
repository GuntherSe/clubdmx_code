#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
class Cuelist

Die Basis für die Cuelist Klasse ist in Cuelistbase definiert. Hier finden sich 
die grundlegenden Attribute und Methoden. In Klasse Cuelist werden die 
Berechnungen des Mix-Outputs gemacht.

"""

import time
import os
import os.path
import threading

from patch import Patch
from ola import OscOla
from cue import Cue
from cuelistbase import Cuelistbase

class Cuelist (Cuelistbase):

    def __init__ (self, patch):
        Cuelistbase.__init__ (self, patch)

        if not Cuelist.running:
            Cuelist.running = True
            Cuelist.fade_thread = threading.Thread (target=Cuelist.run)
            Cuelist.fade_thread.daemon = True
            if not os.environ.get ("PYTHONANYWHERE") == "true":
                Cuelist.fade_thread.start ()

    def __repr__(self):
        return '<Cuelist {}>'.format(self.file.shortname())  

    @classmethod
    def printInstances (cls):
        for instance in cls.instances:
            print (instance)

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


    def is_fading (self) ->bool:
        """ True wenn fading_in oder fading_out """
        if self.is_fading_in or self.is_fading_out:
            return True
        return False

    def tmfactor (self, id:float, tm:"time") -> dict: #, direction:str) -> dict:
        """ Fadefaktor berechnen
        
        id: ID des Cues
        tm: aktuelle Zeit
        return: {in:float zw. 0 und 1, out: Float zw. 0 und 1, xfade:bool}
        """
        infactor = 0.0 # default
        outfactor = 1.0 # default 
        xfade = False # default

        if id in self._idlist:
            # if direction == "in":
            # Zeitfaktor für fade-in:
            waitintm = self.cuedict[id]["Waitin"]
            fadeintm = self.cuedict[id]["Fadein"]
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

            # elif direction == "out":
            # Zeitfaktor für Fade-out:
            waitouttm = self.cuedict[id]["Waitout"]
            fadeouttm = self.cuedict[id]["Fadeout"]
            if fadeouttm == -1.0 and waitouttm == 0 and waitintm == 0: 
                # crossfade
                xfade = True
            if fadeouttm == -1.0: # fadeout nicht angegeben, waitouttm > 0
                fadeouttm = self.cuedict[id]["Fadein"]

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
        else:
            outfactor = 0.0  

        # fade-in abgeschlossen (fade-in + wait-in) und 
        # fade-out abgeschlossen (wait-out + fade-out):
        if (tm > self.start_tm + waitintm + fadeintm) \
                and tm > (self.start_tm + waitouttm + fadeouttm): 
            self.fading_done = True
        else:
            self.fading_done = False

        return {"in":infactor, "out":outfactor, "xfade":xfade}


    def calc_cuecontent (self, tm:"time"):
        """ aktuellen Content berechnen 

        outcue._cuecontent berechnen, wird permanent durchgeführt, siehe self.run()
        tm = aktuelle Zeit 
        hängt ab von: start_tm, tm, currentcue, nextcue

        """
        if (not self.is_starting) and (self.is_paused or self.level == 0): 
            # Pause - keine Auswertung
            self.update_cuelist ()
            return

        # Multiplikator berechnen:
        curfactor = self.tmfactor (self.nextid, tm) #, "out")
        # nextfactor = self.tmfactor (self.nextid, tm, "in")
        # if curfactor["xfade"] == True: # crossfade
        #     self.is_fading_out = self.is_fading_in
            # curfactor["out"] = 1 - curfactor["in"]

        # Übergänge berechnen:

        # 1. items, die nur in currentcue vorkommen:
        if self.is_fading_out: # and not (itemkey in self.nextkeys):
            self.fadeout_percent = int (curfactor["out"] * 100)
            only_out = [i for i in self.currentkeys \
                if i not in self.nextkeys]
            for item in only_out:
                curindex  = self.currentkeys.index (item)
                curlevel = int (self.currentlevels[curindex])
                level = curfactor["out"] * curlevel
                cueitem = self.currentcue.content[curindex]
                self.outcue.line_to_cuecontent ([cueitem[0],cueitem[1],
                        str(int(level))])

        # 2. items, die nur in nextcue vorkommen:
        if self.is_fading_in:
            self.fadein_percent = int (curfactor["in"] * 100) 
            only_in = [i for i in self.nextkeys \
                if i not in self.currentkeys]
            for item in only_in :
                nextindex = self.nextkeys.index (item)
                nextlevel = int (self.nextlevels[nextindex])
                level = curfactor["in"] * nextlevel
                cueitem = self.nextcue.content[nextindex]
                self.outcue.line_to_cuecontent ([cueitem[0],cueitem[1],
                        str(int(level))])

        # 3. items, die in currentcue und nextcue vorkommen:
        if self.is_fading_in and self.is_fading_out:
            intersect = [i for i in self.nextkeys \
                if i in self.currentkeys]
            for item in intersect:
                curindex  = self.currentkeys.index (item)
                nextindex = self.nextkeys.index (item)
                nextlevel = int (self.nextlevels[nextindex])
                curlevel = int (self.currentlevels[curindex])
                if curfactor["xfade"] == True: # crossfade
                    level = curlevel + curfactor["in"] * (nextlevel - curlevel)
                else: # max aus fadeout und fadein
                    level = max (curlevel * curfactor["out"],  
                                nextlevel * curfactor["in"] )
                cueitem = self.currentcue.content[curindex]
                self.outcue.line_to_cuecontent ([cueitem[0],cueitem[1],
                    str(int(level))])
        
        #Test:
        # print (f"\rxFade: {self.fadein_percent} {self.fadeout_percent}", end='')

        # current Cue und next Cue evtl updaten:
        # if self.is_fading_in and curfactor["in"] == 1: # Fading-in done
        #     self.is_fading_in = False
        #     self.is_starting = False
        # if self.is_fading_out and curfactor["out"] == 0:
        #     self.is_fading_out = False
        # fading_done = (not self.is_fading_in) and (not self.is_fading_out)
        if self.fading_done:
            self.is_fading_in = False
            self.is_starting = False
            self.is_fading_out = False

        if self.fading_done and not self.is_loaded and not self.is_starting:
            self.is_loaded = True
            self.logger.debug ("Fading done.")
            # print ("\rFading Done.\nCMD: ", end='')

            self.fadeout_percent = 100
            self.fadein_percent = 0

            self.update_cuelist () # File-Änderungen prüfen/laden

            # nextcue wird zum currentcue, neuen nextcue einlesen
            self.currentpos = self.nextpos
            self.setcurrentcue (self.currentpos)
            self.current_to_output () # outcue mit currentcue abgleichen
            if self.nextprep == self.nextpos:
                self.increment_nextprep () # nextprep um 1 erhöhen
            # else: nextprep wurde bereits verändert

            # Stay Time:
            staytm = self.cuedict[self.currentid]["Stay"]
            if staytm == -1:
                self.go_time = -1
            else:
                self.go_time = tm + staytm
            
        # Stay-Time abgelaufen:
        if (self.go_time != -1) and (tm > self.go_time):
            if self.is_starting:
                self.is_starting = False
            else:
                self.go_time = -1
            self.go ()


    def go (self, cuenr:str=""):
        """ Fade beginnen und Startzeit speichern 

        cuenr: nächste Cuenr oder '-1' -> go back
        """
        # print ("------------------ GO")
        self.update_cuelist ()
        if self.level == 0:
            return
            
        if self.is_fading (): # aktueller Fade noch nicht abgeschlossen
            self.logger.debug ("GO between...")
            self.output_to_current ()

        if cuenr == "": # next nicht angegeben
            # nextprep wurde bei calc_cuecontent erhöht.
            # wenn set_nextprep aufgerufen und cuenr == currentcue
            if not self.is_paused:
                if self.is_fading (): 
                    self.increment_nextprep ()
            # bei GO nach Pause bleibt nextpos gleich
            self.logger.debug ("GO next...")
        elif cuenr == "-1": # go back
            if self.is_paused:
                # self.nextpos = self.currentpos
                self.nextprep = self.currentpos
            elif self.is_fading ():
                self.nextprep = self.currentpos
            else:
                self.decrement_nextprep () # eine pos retour
            self.logger.debug ("GO back...")
        else: # nächste cuenr angegeben
            ret = self.set_nextprep (cuenr)
            if ret:
                self.logger.debug (f"GO to {cuenr}...")
            else:
                return

        if self.is_paused:
            self.start_tm = time.time () - self.elapsed_tm
            self.is_paused = False
            self.logger.debug ("Pause aus...")
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
        else:
            self.go ()


    def output_to_current (self):
        """output Cue wird current Cue, wenn GO während fading_in 
        getriggert wird
        """
        self.logger.debug ("output to current")
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
        Contrib aktualisieren
        """
        self.logger.debug ("current to output")
        # self.outcue.content[:] = [item for item in self.currentcue.content]
        outkeys = [line[0]+'-'+line[1] for line in self.currentcue.content]
        for key in Cue.contrib.contribs[self.outcue.count].copy().keys():
            if key != "faderlevel" and key not in outkeys:
                Cue.contrib.remove_key (self.outcue.count, key)
        # self.outcue.content[:] = [item for item in self.outcue.content \
        #     if item[0]+item[1] in self.currentkeys]
        # self.outcue.content.clear ()

# --- Test -----------------------------------------------------------------
if __name__ == "__main__":
    """ Test Cuelist:
    """
    import pprint # pretty print


    os.chdir ("C:\\Users\\Gunther\\OneDrive\\Programmierung\\clubdmx_rooms\\develop")
    print ("ich bin hier: ", os.getcwd())
    patch = Patch()
    patch.set_path (os.getcwd())
    patch.open ("LED stripe dimmer")

    ola   = OscOla ()
    ola.set_ola_ip ("192.168.0.11")
    print("Verbinde zu OLA-device: {0}".format (ola.ola_ip))
    ola.start_mixing()

    patch.set_universes (2)
    Cue.set_path (os.getcwd())
    Cuelist.set_path (os.getcwd())

    list1 = Cuelist (patch)
    list1.open ("list1")
    list1.level = 0.0

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
            v = Level = 0
            f = Level = 1
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
                print (f"next id:{list1.nextid}, ", end='')
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
            elif i == 'v':
                list1.level = 0
            elif i == 'f':
                list1.level = 1
            else:
                pass
    finally:
        print ("bye...")

