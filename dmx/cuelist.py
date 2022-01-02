#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
class Cuelist

Die Basis für die Cuelist Klasse ist in Cuelistbase definiert. Hier finden sich die
grundlegenden Attribute und Methoden. In Klasse Cuelsit werden die Berechnungen
des Mix-Outputs gemacht.

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
from cuelistbase import Cuelistbase



class Cuelist (Cuelistbase):

    def __init__ (self, patch):
        Cuelistbase.__init__ (self, patch)

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


    def tmfactor (self, id:float, tm:"time", direction:str) -> dict:
        """ Fadefaktor berechnen
        
        id: ID des Cues
        tm: aktuelle Zeit
        direction: 'in' oder 'out'
        return: {in:float zw. 0 und 1, out: Float zw. 0 und 1}
        """
        infactor = 0.0 # default
        outfactor = 1.0 # default 
        xfade = False # default

        if id in self._idlist:
            if direction == "in":
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

            elif direction == "out":
            # Zeitfaktor für Fade-out:
                waitouttm = self.cuedict[id]["Waitout"]
                fadeouttm = self.cuedict[id]["Fadeout"]
                if fadeouttm == -1.0 and waitouttm == 0: # crossfade
                    xfade = True
                    # outfactor wird nicht benötigt
                elif fadeouttm == -1.0: # fadeout nicht angegeben
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
        return {"in":infactor, "out":outfactor, "xfade":xfade}


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
        if curfactor["xfade"] == True: # crossfade
            self.is_fading_out = self.is_fading_in
            curfactor["out"] = 1 - nextfactor["in"]

        # Übergänge berechnen:
        # 1. items, die in nextcue vorkommen:
        if self.is_fading_in:
            self.fadein_percent = int (nextfactor["in"] * 100) 
            for item in self.nextcue.cuecontent ():
                itemkey = item[0] + item[1] # head + attribute
                nextlevel = int (item[2])
                if itemkey not in self.currentkeys: # Fade in 
                    level = nextfactor["in"] * nextlevel
                elif curfactor["xfade"] == True: # crossfade
                    index = self.currentkeys.index (itemkey)
                    curlevel = int (self.currentlevels[index])
                    level = curlevel + nextfactor["in"] * (nextlevel - curlevel)
                else: # max aus fadeout und fadein
                    index = self.currentkeys.index (itemkey)
                    curlevel = int (self.currentlevels[index])
                    level = max (curlevel * curfactor["out"],  
                                nextlevel * nextfactor["in"] )

                self.outcue.line_to_cuecontent ([item[0],item[1],
                    str(int(level))])
                # print (f"Fading in: {item[0]} {item[1]} {int(level)}")
        
        # 2. items, die nur in currentcue vorkommen:
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
            self.go_time = -1
            self.go ()


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
                if self.nextprep == self.currentpos: # next nicht angegeben
                    self.increment_nextprep ()
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
        Contrib aktualisieren
        """
        self.outcue.content[:] = [item for item in self.currentcue.content]
        outkeys = [line[0]+'-'+line[1] for line in self.outcue.content]
        for key in Cue.contrib.contribs[self.outcue.count].copy().keys():
            if key != "faderlevel" and key not in outkeys:
                Cue.contrib.remove_key (self.outcue.count, key)

        # self.outcue.content[:] = [item for item in self.outcue.content \
        #     if item[0]+item[1] in self.currentkeys]


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
    list1.level = 1.0

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

