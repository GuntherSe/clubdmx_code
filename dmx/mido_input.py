#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" MIDI Input """

# import pygame
# import pygame.midi
import mido
import threading
import time

import midi_devices as mdev
from mido_output import MidiDevice, MidiOutput

TEST = False

class Midi (MidiOutput, threading.Thread):
    """ class Midi 

    Evaluierung als callback ausführen 
    """

    paused = False
    pause_cond = threading.Condition (threading.Lock ())

    def __init__ (self):
        threading.Thread.__init__ (self, target=self.run)
        MidiOutput.__init__ (self)

        self.setDaemon (True)

        self.in_ports = [MidiDevice() for i in range (4)] # verwendete Geräte
        self.in_buttons = [{} for i in range (4)] # verwendete Buttons
        self.in_faders = [{} for i in range (4)] # verwendete Fader

        self.start ()


    def run (self):
        """ thread starten
        """
        while True:
            with Midi.pause_cond:
                while Midi.paused:
                    Midi.pause_cond.wait ()

                for i in range (4):
                    if self.in_ports[i].port:    
                        for msg in  self.in_ports[i].port.iter_pending ():
                            self.in_ports[i].eval_msg (msg)
            time.sleep (0.02)

    # def run (self):
    #     """ callback an die in_ports zuweisen
    #     """
    #     self.paused = False
    #     for i in range (4):
    #         if self.in_ports[i].device_id != -1:
    #             self.in_ports[i].port.callback = self.in_ports[i].receive

    @classmethod
    def pause (cls):
        """ thread pausieren 
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

        for i in range (4):
            if self.in_ports[i].device_id != -1:
                self.in_ports[i].set_eval_function (newfunc)


    def clear (self, pos:int):
        """ self.in_ports[pos] zurücksetzen
        """
        if 0 <= pos < 4:
            self.in_ports[pos].clear ()
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
        return: {"message":str, "category": "error" oder "success"}
        """
        ret = {}
        ret["category"] = "danger"
        if 0 <= pos < 4:
            newdev = self.in_ports[pos] # MidiDevice 
        else:
            ret["message"] = f"{pos} nicht gültig."
            return ret

        # midi_device bereits zugewiesen:
        if newdev.device_id == num: # keine Änderung
            ret["message"] = "keine Änderung."
            ret["category"] = "success"
            return ret

        if newdev.device_id != -1 : # midi_device vorhanden
            newdev.clear ()

        devlist = self.list_devices ("input")
        if devlist and num != -1: # input Gerät
            msg = newdev.set_device (devlist, num)
            if msg["result"] == "true":
                newdev.index = pos
                # newdev.port.callback = newdev.receive
                ret["message"] = msg["name"]
                ret["category"] = "success"
            else:
                self.clear (pos)
                ret["message"] = f"Midi-Input-Gerät {num} belegt"

        else:
            self.clear (pos)
            ret["message"] = f"Midi-Input-Gerät {num} nicht zugewiesen"
        return ret


    def receive_midi (self, msg):
        """ midi-input mittels eval weiterverarbeiten

        msg: mido Message
        eval: print oder andere eval-Funktion
        """
        print (msg.bytes ())


        # for i in range (len (self.in_ports)): # alle MidiInputs
        #     device = self.in_ports[i]

        #     if pygame.midi.get_init () and \
        #         device.midi_device and device.device_id != -1:
        #         if device.midi_device.poll():
        #             msg = device.midi_device.read(100) # mehrere messages einlesen, sonst träge
        #             if TEST:
        #                 print (msg)
        #             msglen = len(msg) # anzahl midi-messages
        #             for cnt in range (msglen):
        #                 controller = msg[cnt][0][1]
        #                 value = msg[cnt][0][2]
        #                 if controller in device.faders: # fader gefunden
        #                     fader = device.faders.index (controller)
        #                     if value != device.fader_buffer[fader]:
        #                         device.fader_buffer[fader] = value
        #                         device.fader_update[fader] = 1
        #                 elif controller in device.buttons: # button
        #                     button = device.buttons.index(controller)
        #                     self.eval (i, "button", button, value)
        #                     # print (button, value)
        #             for cnt in range (len(device.fader_update)):
        #                 if device.fader_update[cnt] == 1:
        #                     device.fader_update[cnt] = 0
        #                     self.eval (i, "fader", cnt, device.fader_buffer[cnt])



# --- Test -------------------------------------------------------------------
if __name__ == "__main__":
    
    # TEST = True

    infotxt = """
---- MIDI Input Test -----

Kommandos: x = Exit
           # = zeige diese Info 

           i = zeige alle MIDI-input-Geräte
           o = zeige alle MIDI-output-Geräte
           <pos> <num> = verwende MIDI Input <num> an Gerät <pos>
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
            elif i == 'q':
                mididev.pause ()
                print ("pause")
            elif i == 'w':
                mididev.resume ()
                print ("resume")
            
            elif i == 'i':
                ret = mididev.list_devices ("input")
                for item in ret:
                    print (item)
            elif i == 'o':
                ret = mididev.list_devices ("output")
                for item in ret:
                    print (item)
            elif i == 's':
                for dev in mididev.in_ports:
                    print (dev)

            elif cmd[0] == 'k':
                try:
                    ret = mididev.set_indevice (int(cmd[1]), -1)
                except:
                    ret = mididev.set_indevice (0, -1)
                print (ret)

            else:
                try:
                    ret = mididev.set_indevice (int(cmd[0]), int(cmd[1]))
                    print (ret)
                except:
                    pass

    finally:
        print ("exit...")



