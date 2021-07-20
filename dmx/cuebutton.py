#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
class Cuebutton
für Cues ohne Fader, sondern als Schalter mit fade-in und fade-out

"""

import time
import csv
import os
import os.path
import threading

from csvfileclass import Csvfile

from patch import Patch
from ola import OscOla
from cue import Cue



class Cuebutton (Cue):

    instances = []
    timeout = 0.02
    running = False
    
    def __init__ (self, patch):
        Cue.__init__ (self, patch)
        self.__class__.instances.append (self)
        self.fade_in = 3.0
        self.fade_out = 5.0
        self.type = "Schalter" # Schalter, Taster, Auswahl
        self.group = 0 # 0 bis 10
        self.is_fading = False
        self.direction = "up" # "up" oder "down"
        self.start_tm = 0.0
        self.status = 0 # 0 -> losgelassen, 1 -> gedrückt

        if not Cuebutton.running:
            Cuebutton.running = True
            Cuebutton.fade_thread = threading.Thread (target=Cuebutton.run)
            Cuebutton.fade_thread.setDaemon (True)
            if not os.environ.get ("PYTHONANYWHERE") == "true":
                Cuebutton.fade_thread.start ()

    def __repr__(self):
        return '<Cuebutton {}, {}>'.format(self.count, self.file.shortname())  

    # def __del__(self):
    #     self.__class__.instances.pop (self)
    #     return super().__del__()

    @classmethod
    def printInstances (cls):
        for instance in cls.instances:
            print (instance)

    @classmethod 
    def run (cls):
        """ Kalkulations-loop """
        while True:
            cls.calc_all_faders ()
            time.sleep (cls.timeout)

    @classmethod
    def calc_all_faders (cls):
        """ alle Faderlevel berechnen 
        """
        tm = time.time ()
        try:
            for instance in cls.instances:
                instance.calc_fader (tm)
        except: # instances-Liste kann neu erzeugt werden
            pass


    @classmethod
    def radio_buttons_off (cls, group):
        """ Alle Buttons mit Type 'Auswahl' und Gruppe 'group' off
        """
        for instance in cls.instances:
            if instance.type == "Auswahl" and instance.group == group \
                and instance.status: 
                instance.off ()


    @classmethod
    def items (cls, location:str) ->list:
        """ alle buttons mit location==location in dictlist
        """
        ret = []
        for inst in cls.instances:
            if inst.location == location:
                item = {}
                item["Text"] = inst.text
                item["Filename"] = inst.file.shortname()
                item["Type"] = inst.type
                item["Group"] = inst.group
                item["Fade_in"] = inst.fade_in
                item["Fade_out"] = inst.fade_out
                item["Index"] = cls.instances.index (inst)
                ret.append (item)
        return ret


    # def radio_buttons_off (self, group):
    #     """ Alle Buttons mit Type 'Auswahl' und Gruppe 'group' off
    #     """
    #     for but in Cuebutton.instances:
    #         if but.type == "Auswahl" and but.group == group \
    #             and but.status : 
    #             but.off ()

    def calc_fader (self, tm:"time"):
        """ Faderlevel berechnen 
        tm = aktuelle Zeit 
        """
        if self.is_fading:
            if self.direction == "up":
                # tm = current_tm + self.start_level * self.fade_in
                if self.fade_in != 0 and tm < self.start_tm + self.fade_in:
                    self.level = (tm-self.start_tm) / self.fade_in
                else:
                    self.is_fading = False
                    self.level = 1
            else: # down
                # tm = current_tm + (1 - self.start_level) * self.fade_out
                if self.fade_out != 0 and tm < self.start_tm + self.fade_out:
                    self.level = 1 - (tm-self.start_tm) / self.fade_out
                else:
                    self.is_fading = False
                    self.level = 0


    def off (self) -> int:
        """ Button OFF
        Fade-out ist abhängig vom fade-Status 
        """
        self.status = 0
        self.direction = "down"
        if not self.is_fading:
            self.is_fading = True
            self.start_tm = time.time ()
        else: # is_fading
            self.start_tm = time.time () - self.fade_out * (1-self.level)
        return 0


    def go (self) ->int:
        """ Fade beginnen und Startzeit speichern 
        Falls gerade gefadet wird, die Fade-Richtung umdrehen
        und fiktive start_tm entsprechend dem Faderlevel berechnen
        return: 1 für direction == up, 0 für direction == down
        """
        if not self.is_fading:
            self.is_fading = True
            self.start_tm = time.time ()
            if self.level == 0:
            # type == "Auswahl" -> alle cuebuttons mit gleicher group ändern:
                if self.type == "Auswahl":
                    Cuebutton.radio_buttons_off (self.group)
                self.direction = "up"
                self.status = 1
            else:
                self.direction = "down"
                self.status = 0
        else:
            # Richtung wechseln:
            if self.direction == "up":
                self.direction = "down"
                self.status = 0
                self.start_tm = time.time () - self.fade_out * (1-self.level)
            else:
            # type == "Auswahl" -> alle cuebuttons mit gleicher group ändern:
                if self.type == "Auswahl":
                    Cuebutton.radio_buttons_off (self.group)
                self.direction = "up"
                self.status = 1
                self.start_tm = time.time () - self.fade_in * self.level
        # self.link ()
        return self.status


    # def link (self):
    #     """ alle Buttons mit Link-Kriterien synchronisieren
    #     Kriterien: text, _file
    #     synchronisiert wird: is_fading, start_tm, direction, status
    #     anderes wird nicht synchronisiert.
    #     """
    #     for but in Cuebutton.instances:
    #         if self != but and self.text and self.text == but.text \
    #                     and self.file._file == but.file._file:
    #             but.is_fading = self.is_fading
    #             but.start_tm  = self.start_tm
    #             but.direction = self.direction
    #             but.status    = self.status



# --- Test -----------------------------------------------------------------
if __name__ == "__main__":
    """ Test Cuebutton:
    Fadezeiten, Button-Type und Button-Group werden nicht berücksichtigt.
    Weitere Tests: 'test cuebutton.py'
    """
    import pprint # pretty print


    os.chdir ("C:\\Users\\Gunther\\OneDrive\\Programmierung\\clubdmx_rooms\\test")
    print ("ich bin hier: ", os.getcwd())
    patch = Patch("LED stripe")
    ola   = OscOla ()
    ola.set_ola_ip ("192.168.0.11")
    print("Verbinde zu OLA-device: {0}".format (ola.ola_ip))
    ola.start_mixing()

    patch.set_universes (2)

    cue1 = Cuebutton (patch)
    cue1.open ("led stripe red")
    cue2 = Cuebutton (patch)
    cue2.open ("led stripe blue")
    cue2.fade_out = 10.0
    cue2.fade_in = 10.0

    cuelist = [cue1, cue2]
    pp = pprint.PrettyPrinter(depth=6)


    infotxt = """
    ---- Lichtpult Cue Test -----

    Kommandos: x = Exit
            # = zeige diese Info 
            c = Zeige Cuelist 1
            i = Zeige Infos zu Cuebuttons
            m = Zeige Mix Universum 1

            1 = GO Button 1
            2 = GO Button 2

    """

    print (infotxt)
    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
            elif i == 'c':
                pp.pprint (cue1.cuelist())
            elif i == 'm':
                uni = 1 # input ("Universum: ")
                print (patch.show_mix(uni))
            elif i == 'i':
                Cuebutton.printInstances ()
            elif i == '1':
                ret = cue1.go ()
                print (ret)
            elif i == '2':
                ret = cue2.go ()
                print (ret)
            else:
                pass
    finally:
        print ("bye...")

