#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" MIDI Output """

import pygame
import pygame.midi
import threading
import time

import midi_devices as mdev
from midioutput import MidiDevice, MidiOutput

TEST = False

class Midi (MidiOutput, threading.Thread):
    """ class Midi 

    Evaluierung als Thread ausführen 
    """

    paused = False
    pause_cond = threading.Condition (threading.Lock ())

    def __init__ (self):
        threading.Thread.__init__ (self, target=self.run)
        MidiOutput.__init__ (self)

        self.setDaemon (True)

        # self.index  = index # für die Eval-Funktion als Erkennung
        self.eval = print   # Auswertung des Midi-Inputs

        self.in_devices = [MidiDevice() for i in range (4)] # verwendete Geräte
        self.in_buttons = [{} for i in range (4)] # verwendete Buttons
        self.in_faders = [{} for i in range (4)] # verwendete Fader

        # Thread starten:
        self.start ()


    def run (self):
        """ thread starten 
        """
        while True:
            with Midi.pause_cond:
                while Midi.paused:
                    Midi.pause_cond.wait ()

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

    def clear (self, pos:int):
        """ self.in_devices[pos] zurücksetzen
        """
        if 0 <= pos < 4:
            self.in_devices[pos].clear ()
        else:
            return f"{pos} nicht gültig."


    def clear_lists (self):
        """ Listen der verwendeten Fader und Buttons leeren 
        """
        self.in_buttons = [{} for i in range (4)] # verwendete Buttons
        self.in_faders = [{} for i in range (4)] # verwendete Fader
        self.out_buttons = [[] for i in range (4)] # verwendete Buttons
        self.out_faders = [[] for i in range (4)] # verwendete Fader


    def set_indevice (self, pos:int, num:int) ->str:
        """ Midigerät zuweisen
        
        pos: Position in self.out_devices, 0 <= pos < 4
        num: Devicenummer neu oder ändern
        """
        if 0 <= pos < 4:
            newdev = self.in_devices[pos] # MidiDevice 
        else:
            return f"{pos} nicht gültig."

        if self.check_devicenum (num, "all"):
            # midi_device bereits zugewiesen:
            if newdev.device_id == num: # keine Änderung
                return {"keine Änderung."}

            if newdev.midi_device: # midi_device vorhanden
                newdev.clear ()

            devlist = self.check_devicenum (num, "input")
            if devlist: # input Gerät
                ret = newdev.set_device (devlist, num)
                # buffer anlegen:
                fadercount = len (newdev.faders)
                newdev.fader_buffer = [0 for i in range (fadercount)]
                newdev.fader_update = [0 for i in range (fadercount)]

        else:
            self.clear (pos)
            ret = "Fehler beim Zuordnen von Midi-Device"
        return ret


    def receive_midi(self):
        """ midi-input mittels eval weiterverarbeiten
        eval: print oder andere eval-Funktion
        """
        for i in range (len (self.in_devices)): # alle MidiInputs
            device = self.in_devices[i]

            if device.midi_device and device.device_id != -1:
                if device.midi_device.poll():
                    msg = device.midi_device.read(100) # mehrere messages einlesen, sonst träge
                    if TEST:
                        print (msg)
                    msglen = len(msg) # anzahl midi-messages
                    for cnt in range (msglen):
                        controller = msg[cnt][0][1]
                        value = msg[cnt][0][2]
                        if controller in device.faders: # fader gefunden
                            fader = device.faders.index (controller)
                            if value != device.fader_buffer[fader]:
                                device.fader_buffer[fader] = value
                                device.fader_update[fader] = 1
                        elif controller in device.buttons: # button
                            button = device.buttons.index(controller)
                            self.eval (i, "button", button, value)
                            # print (button, value)
                    for cnt in range (len(device.fader_update)):
                        if device.fader_update[cnt] == 1:
                            device.fader_update[cnt] = 0
                            self.eval (i, "fader", cnt, device.fader_buffer[cnt])



# --- Test -------------------------------------------------------------------
if __name__ == "__main__":
    
    # TEST = True

    infotxt = """
---- MIDI Input Test -----

Kommandos: x = Exit
           # = zeige diese Info 

           a = zeige alle MIDI-Geräte
           i = zeige alle MIDI-input-Geräte
           o = zeige alle MIDI-output-Geräte
           <num> = verwende MIDI Input <num>
           <pos> <num> = verwende MIDI Output <num> an Gerät <pos>
           k <pos> = verwende kein MIDI an Gerät <pos>
"""

    mididev = Midi ()
    # midiout = MidiOutput ()
    print (infotxt)

    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            cmd = i.split ()
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
            elif i == 's':
                for dev in mididev.in_devices:
                    print (dev)

            elif cmd[0] == 'k':
                try:
                    ret = mididev.set_indevice (int(cmd[1]), -1)
                except:
                    ret = mididev.set_indevice (0, -1)
                print (ret)

            else:
                try:
                    ret = mididev.set_device (int(cmd[0]), int(cmd[1]))
                    print (ret)
                except:
                    pass

    finally:
        print ("exit...")



