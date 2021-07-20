#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" class Contrib: Sammelt HTP-Werte/LTP-Werte und verarbeitet das
Maximum jedes Keys.
Struktur von contribs: 
{
    index1: {key1-1: [tm1-1, val1-1, val1-2, ...], 
             key1-2: [tm1-2, val2-1, val2-2, ...],
             ...},
    index2: {key2-1: [tm2-1, val2-1, val2-2, ...], 
             key2-2: [tm2-2, val2-1, val2-2, ...],
             ...},
    index3: ...
}

index: definiert die Herkunft des Eintrags in contribs, z.B Fadernummer
key: entspricht in der Anwendung im Cue.Mix 'Head-Attribute'
    bzw. Level = Faderlevel
tm: Zeitpunkt des Eintrags in contribs
val: der von der Herkunft[index] angeforderte Wert für 'Head-Attribute'
"""

import threading
import time
import random

class Contrib (threading.Thread):
    """ sammelt Beiträge zur Auswertung
- Methoden: add, remove_index, remove_val 
"""

    def __init__(self):
        threading.Thread.__init__ (self, target=self.run)
        self.paused = False
        self.pause_cond = threading.Condition (threading.Lock ())
        self.setDaemon (True)

        self.contribs = {}
        self.output_function = print
        # output_function: den Mix an output schicken
        self.mix_function = self.no_mix
        # mix_function: contrib nach Kriterien bewerten, Mix erstellen
        self._sleep = 2


    def len (self):
        return len (self.contribs)

    def set_sleeptime (self, t):
        """ Sleep-Zeit in Mixschleife """
        
        self._sleep = t

    def add (self, index, *args) -> list:
        """ val in self.contribs eintragen

        nur unterschiedliche [index,val] werden eingetragen
        val als int eintragen, nicht str
        """
        key = args[0]
        # print ("Index: {}, Key: {}".format (index,key))
        if index not in self.contribs.keys(): # index nicht vorhanden
            self.contribs[index] = {}

        values = [arg for arg in args]
        values = values [1:] # key entfernen
        self.contribs[index][key] = values

        # print ("contrib.add: ", index, key, values)
        # return (index, key, values)


    def remove_index (self, index):
        """ index aus _contrib entfernen

        vorher pro key: 0 an Mix schicken
        """
        if index in self.contribs:
            # vor Entfernen aktualisieren / auf 0 setzen:
            self.mix_function ()
            time.sleep (self._sleep)
            self.contribs.pop  (index, None)

    def contrib(self):
        """ contribs zeigen
        """
        return self.contribs


    def to_dictlist(self) ->list:
        """ contrib in Liste, dict pro Zeile
        zur Tabellenansicht
        Zeile: {index:val1, key:val2, level:val3, time:val4}
        Output: [Zeile-1, Zeile-2, ... , Zeile-n]
        """
        ret = []
        for index in self.contribs.keys():
            data = self.contribs[index]
            for key in data.keys():
                retline = {}
                retline["index"] = index
                retline["key"] = key
                retline["level"] = data[key][0]
                retline["extra"] = data[key][1]
                ret.append (retline)
        return ret


    def set_output_function(self, newfunc):
        """ contrib-Mix an output schicken
        """
        self.output_function = newfunc
        

    def set_mix_function(self, newfunc):
        """ die Verarbeitung der Contrib-Daten zuweisen
        """
        self.mix_function = newfunc
        

    def run (self):
        """ Mixfunktion in loop ausführen 
        """
        while True:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait ()
                self.mix_function ()
            time.sleep (self._sleep)


    def pause (self):
        """ pausiere self.thread
        """
        if not self.paused:
            self.paused = True
            self.pause_cond.acquire ()

    def resume (self):
        """ Pausenende self.thread
        """
        if self.paused:
            self.paused = False
            self.pause_cond.notify ()
            self.pause_cond.release ()

    
# ----- Mix Funktionen ----------------------------------------------------

    def no_mix (self):
        """ default Mix-Funktion
        """
        pass


    def test_mix (self):
        """ Mixfunktion zum Test von Contrib """
        tempmix = {}
        # while self.__mixing:
        for index in self.contribs.keys():
            # ich brauche: faderlevel, attrib_level, attrib_type=htp/ltp
            for key in self.contribs[index].keys():
                val = int (self.contribs[index][key][0])
                if key in tempmix.keys():
                    tempmix[key] = max (tempmix[key],  val)
                else:
                    tempmix[key] = val

        for key in tempmix.keys():
            self.output_function (key, tempmix[key])
        # print ("tempmix: ", tempmix)


    def cue_mix (self):
        """ Das ist die Mix-Funktion, die htp und ltp berücksichtigt
        
        Brauche daher:  type = HTP/LTP
                        Faderlevel
                        Max-level für das Attribut (laut cue.csv)
        """
        tempmix = {}
        tempmix.clear()
        # key = 'faderlevel' oder 'Head-Attr'
        # tempmix[key]: 
        #    für HTP (dmx-Wert, letzte fadetime, 0)
        #    für LTP (dmx-Wert, letzte fadetime, letzter fadelevel)
        #    für TOP (dmx-Wert, letzte fadetime, -1)
        for index in self.contribs.copy().keys():
            # ich brauche faderlevel:
            if "faderlevel" not in self.contribs[index].keys():
                # Defaultwert setzen:
                faderlevel = 0.0
                fadertime = time.time()
                self.add (index, "faderlevel", faderlevel, fadertime)
            else:
                faderlevel = self.contribs[index]["faderlevel"][0]
                fadertime  = self.contribs[index]["faderlevel"][1]

            # ich brauche attrib_level, attrib_type=HTP/LTP/vLTP:
            for key in self.contribs[index].keys():
                data = self.contribs[index][key]
                # data: wenn key==Head-Attrib -> [att_level, att_type] 
                #       wenn key==faderlevel  -> [level, time]
                if data[1] == "HTP":
                    newlevel = faderlevel * int(data[0])
                    if key in tempmix.keys() : 
                        if tempmix[key][2] != -1: #kein topcue
                            dmxval = max (tempmix[key][0], newlevel)
                            tempmix[key] = (dmxval, fadertime, 0)
                    else:
                        tempmix[key] = (newlevel, fadertime, 0)

                elif (data[1] == "LTP" or data[1] == "vLTP"):
                    if key in tempmix.keys() : # key hat schon einen Wert
                        if tempmix[key][2] != -1: #kein topcue
                            oldtime = tempmix[key][1]
                            if fadertime > oldtime:
                                latest_time  = fadertime
                                # latest_level = faderlevel
                                # dmxval = latest_level * int(data[0]) + \
                                #         (1 - latest_level) * tempmix[key][0]
                            else:
                                latest_time  = oldtime
                                # latest_level = tempmix[key][2]
                                # dmxval = (1 - latest_level) * int(data[0]) + \
                                #         latest_level * tempmix[key][0]
                            # tempmix[key] = (dmxval, latest_time, latest_level)
                            dmxval = faderlevel * int(data[0]) + \
                                        (1 - faderlevel) * tempmix[key][0]
                            tempmix[key] = (dmxval, latest_time, faderlevel)

                    else:
                        newlevel = faderlevel * int(data[0])
                        tempmix[key] = (newlevel, fadertime, faderlevel)

                elif (data[1] == "TOP"): # topcue
                    newlevel = faderlevel * int(data[0])
                    # Wert überschreiben
                    tempmix[key] = (newlevel, fadertime, -1)

                else:
                    pass

        # an output schicken:
        for key in tempmix.keys():
            # print ("contrib.mix: ", key, tempmix[key][0])
            self.output_function (key, int (tempmix[key][0]))


# ---------------------------------------------------------------------
# Unit Test:        

if __name__ == "__main__":

    infotxt = """
---- Test  -----
Kommandos: x = Exit
           # = zeige diese Info 
           h = Set mixtype 'HTP'
           l = Set mixtype 'LTP'
           t = Test-Mix
           m = Loop Mix

           p = Pause
           w = weiter mit dem Mix
           
           1 = Zeige contrib
           2 = add contrib zu Index 1
           3 = remove index aus contrib
           4 = diverse Werte add
           5 = contrib leeren
           6 = diverse Werte add
           7 = zeige contrib.dictlist

           f1 = Fade 1 up
           f2 = Fade 2 up
           d1 = Fade 1 down
           d2 = Fade 2 down
"""
    contrib = Contrib() 
    contrib.set_mix_function (contrib.cue_mix)
    mixtype = 'LTP'
    # contrib.start_mixing ()


    def fade (index:int, start:float, stop:float) :
        """ Test Fader """
        step = (stop-start) / 5 # kann auch negativ sein
        print ("Start: ", start)
        tm = time.time()
        contrib.add (index, "faderlevel", start, tm)
        contrib.mix_function()

        for i in range (5) :
            tm = time.time()
            contrib.add (index, "faderlevel", start+(step*(1+i)),tm)
            contrib.mix_function()
        print ("Stop: ", stop)


    print (infotxt)
    
    # faderlevel für Test von cue_mix auf 1.0:
    tm = time.time()
    contrib.add (1, "faderlevel", 0.0, tm)
    contrib.add (2, "faderlevel", 0.0, tm)
    # contrib.add (3, "faderlevel", 0.0, tm)
    # contrib.add (4, "faderlevel", 0.0, tm)


    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
            elif i == 'h':
                mixtype = 'HTP'
            elif i == 'l':
                mixtype = 'LTP'
            elif i == 't': #Mix-Werte
                contrib.mix_function ()
            elif i == 'm':
                contrib.start ()
            elif i == 'p':
                contrib.pause ()
            elif i == 'w':
                contrib.resume ()
            elif i == '1':
                print (contrib.contrib ())
            elif i == '2':
                key = input ("Key: ")
                val1 = input ("Val1: ")
                contrib.add (1, key, val1, mixtype)
            elif i == '3':
                index = input ("Index: ")
                contrib.remove_index (int(index))
            elif i == '4':
                (contrib.add (1,'1-attrib','150',mixtype))
                print (contrib.add (1,'2-attrib','100',mixtype))
                print (contrib.add (2,'1-attrib','40' ,mixtype))
                print (contrib.add (2,'2-attrib','255',mixtype))
            elif i == '5':
                for i in range (4):
                    if (1+i) in contrib.contribs.keys():
                        contrib.remove_index (1+i)
            elif i == '6':
                print (contrib.add (1,'1-attrib','50' ,mixtype))
                print (contrib.add (2,'1-attrib','150',mixtype))
                print (contrib.add (3,'2-attrib','250',mixtype))
                print (contrib.add (4,'2-attrib','250',mixtype))
                print (contrib.add (1,'3-attrib','250',mixtype))
            elif i == '7':
                print (contrib.to_dictlist ())
            elif i == 'f1':
                fade (1, 0.0, 1.0)
            elif i == 'f2':
                fade (2, 0.0, 1.0)
            elif i == 'd1':
                fade (1, 1.0, 0.0)
            elif i == 'd2':
                fade (2, 1.0, 0.0)
            
            else:
                pass
    finally:
        print ("exit...")
