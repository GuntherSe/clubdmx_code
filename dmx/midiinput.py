#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" MIDI Output """

import pygame
import pygame.midi
import threading
import time

import midi_devices as mdev
from midioutput import MidiDevice

class MidiInput (MidiDevice, threading.Thread):
    """ Midi-Input 
    Evaluierung als Thread ausführen 
    """

    paused = False
    pause_cond = threading.Condition (threading.Lock ())

    def __init__ (self, index:int=0):
        threading.Thread.__init__ (self, target=self.run)
        MidiDevice.__init__ (self)

        self.setDaemon (True)

        self.index  = index # für die Eval-Funktion als Erkennung
        self.eval = print   # Auswertung des Midi-Inputs
        self.faders = {}
        self.buttons = {}
        # Liste der Midi-Fader timestamps:
        self.fader_buffer  = []
        self.fader_update  = []

        # Thread starten:
        self.start ()


    def run (self):
        """ thread starten 
        """
        while True:
            with MidiInput.pause_cond:
                while MidiInput.paused:
                    MidiInput.pause_cond.wait ()

                self.receive_midi ()
            time.sleep (0.02)

    
    @classmethod    
    def pause (cls):
        """ pausiere self.thread
        """
        cls.paused = True
        cls.pause_cond.acquire ()

    @classmethod
    def resume (cls):
        """ Pausenende self.thread
        """
        cls.paused = False
        cls.pause_cond.notify ()
        cls.pause_cond.release ()

    def set_eval_function (self, newfunc):
        """ Eval-Funktion zuweisen """
        self.eval = newfunc

    def set_device (self, num:int) ->str:
        devlist = self.list_devices("input")
        devnums = [dev[0] for dev in devlist]
        if num in devnums: # input Gerät
            ret = MidiDevice.set_device (self, num)
            if ret["status"] == "frei":
                if self.name in mdev.midi_device_dict:
                    self.faders  = mdev.midi_device_dict [self.name][0]
                    self.buttons = mdev.midi_device_dict [self.name][1]
                    self.message (f"verwende {self.name}")
                else:
                    self.faders  = mdev.default_faders
                    self.buttons = mdev.default_buttons
                    self.message (f"verwende {self.name} mit 1:1 Zuordnung")
                # buffer anlegen:
                fadercount = len (self.faders)
                self.fader_buffer = [0 for i in range (fadercount)]
                self.fader_update = [0 for i in range (fadercount)]
        else:
            ret = MidiDevice.set_device (self, -1)
        return ret


    def receive_midi(self):
        """ midi-input mittels eval weiterverarbeiten
        eval: print oder andere eval-Funktion
        """

        if self.midi_device and self.device_id != -1:
            if self.midi_device.poll():
                msg = self.midi_device.read(100) # mehrere messages einlesen, sonst träge
                # print (msg)
                msglen = len(msg) # anzahl midi-messages
                for cnt in range (msglen):
                    controller = msg[cnt][0][1]
                    value = msg[cnt][0][2]
                    if controller in self.faders: # fader gefunden
                        fader = self.faders.index (controller)
                        if value != self.fader_buffer[fader]:
                            self.fader_buffer[fader] = value
                            self.fader_update[fader] = 1
                    elif controller in self.buttons: # button
                        button = self.buttons.index(controller)
                        self.eval (self.index, "button", button, value)
                        # print (button, value)
                    else:
                        print ("NanoKontrol: Szene 1 aktiv?")
                for cnt in range (len(self.fader_update)):
                    if self.fader_update[cnt] == 1:
                        self.fader_update[cnt] = 0
                        self.eval (self.index, "fader", cnt, self.fader_buffer[cnt])



# --- Test -------------------------------------------------------------------
if __name__ == "__main__":

    infotxt = """
---- MIDI Input Test -----

Kommandos: x = Exit
           # = zeige diese Info 

           a = zeige alle MIDI-Geräte
           i = zeige alle MIDI-input-Geräte
           o = zeige alle MIDI-output-Geräte
           <num> = verwende MIDI Input <num>
           k = verwende kein MIDI
"""

    mididev = MidiInput ()
    # midiout = MidiOutput ()
    print (infotxt)

    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
            elif i == 'a':
                ret = mididev.list_devices ()
                for item in ret:
                    print (item)
            elif i == 'i':
                ret = mididev.list_devices ("input")
                for item in ret:
                    print (item)
            elif i == 'o':
                ret = mididev.list_devices ("output")
                for item in ret:
                    print (item)
            elif i == 'k':
                ret = mididev.set_device (-1)
                print (ret)

            else:
                try:
                    num = int(i)
                except:
                    num = None
                ret = mididev.set_device (num)
                print (f"Verwende {ret}, {mididev.miditype}")

    finally:
        print ("exit...")



