#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
OSC Input
Erstellen eines OSC-Servers mit folgenden OSC-Strings:

/fader/<number> <faderwert>
/button/<number> 

number: 1 .. 100 (int)
faderwert: 0 .. 1 (float)

Abhängig von der Config-Variablen osc_input wird der Thread aktiviert,
dh. die eval-Funktion wird aktiviert oder deaktiviert
"""

import threading
# import time
from pythonosc import dispatcher
from pythonosc import osc_server


class OscInput (threading.Thread):
    """ OSC Input
    Evaluierung als Thread, (in Pythonanywhere nicht verfügbar)
    siehe auch class MidiInput
    zur Aktivierung genügt EIN Klassen-Objekt
    """

    def __init__ (self, port:int=0):

        self.paused = False  
        self.in_port = port
        self.eval = self.default_eval   # Auswertung des OSC-Inputs

        self.dispatcher = dispatcher.Dispatcher ()
        self.dispatcher.set_default_handler (self.default_handler)

        self.addresses = ["/button", "/exebutton1", "/exebutton2", "/fader",
           "/exefader", "/head", "/clear", "/go", "/pause", "/cuelistfader"]
        for addr in self.addresses:
            self.dispatcher.map (addr, self.eval)

        # Adressen, die mehr als 1 Argument enthalten:
        # für die ersten 10 zusätzliche Mappings im Dispatcher erzeugen
        self.numaddresses = ["/fader", "/exefader", 
            "/go", "/pause", "/cuelistfader"]
        for addr in self.numaddresses:
            for cnt in range (1,11):
                self.dispatcher.map (addr + '/' + str(cnt), self.eval)

        # nur wenn port != 0 server starten:
        self.set_port (self.in_port)


    def default_handler (self, address, *args):
        print(f"DEFAULT {address}: {args}")

    
    def default_eval (self, address, *args):
        if not self.paused:
            print ("--", address, args)


    def pause (self):
        """ pausiere die Auswertung
        """
        if self.paused == False:
            self.paused = True


    def resume (self):
        """ Pausenende 
        """
        if self.paused:
            self.paused = False


    def set_eval_function (self, newfunc):
        """ Eval-Funktion zuweisen 
        """
        for addr in self.addresses:
            self.dispatcher.unmap (addr, self.eval)
            self.dispatcher.map (addr, newfunc)

        for addr in self.numaddresses:
            for cnt in range (1,11):
                self.dispatcher.unmap (addr + '/' + str(cnt), self.eval)
                self.dispatcher.map (addr + '/' + str(cnt), newfunc)

        self.eval = newfunc
        # print ("ok eval.")


    def set_port (self, newport:int):
        """ self.port ändern und server starten"""
        ret = {}
        if not self.in_port:
            self.in_port = newport

            # self.server = osc_server.ThreadingOSCUDPServer ( 
            self.server = osc_server.BlockingOSCUDPServer ( 
                ("0.0.0.0", self.in_port), self.dispatcher)
            threading.Thread.__init__ (self, target=self.server.serve_forever,
                                       daemon=True)
            # self.setDaemon (True)

            # Thread starten:
            self.start ()
            ret["category"]= "success"
            ret["message"] = f"OSC-Server mit Port {self.in_port} gestartet."
            return ret
        else:
            ret["category"]= "danger"
            ret["message"] = \
                f"OSC-Server war schon mit Port {self.in_port} gestartet."
            return ret


# --- unit Test ------------------------------------------------------
if __name__ == "__main__":

    infotxt = """
---- OSC Input Test -----

Kommandos: x = Exit
           # = zeige diese Info 
           p = pause
           r = resume
           e = external eval
           d = default eval
           n = neuer Port:8800 

"""

    def external_eval (address:str, *args):
        print ("external", address, args)

    oscin = OscInput ()
    
    print (infotxt)

    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
            elif i == 'p':
                oscin.pause ()
            elif i == 'r':
                oscin.resume ()
            elif i == 'e':
                oscin.set_eval_function (external_eval)
            elif i == 'd':
                oscin.set_eval_function (oscin.default_eval)
            elif i == 'n':
                ret = oscin.set_port (8800)
                print (ret)

    finally:
        print ("exit...")



