#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" MIDI Input """

# import mido
import threading
import time

# import midi_devices as mdev
from mido_output import MidiDevice, MidiOutput
from usbmonitor import USBMonitor
# see: https://pypi.org/project/usb-monitor/
# from usbmonitor.attributes import ID_MODEL


class Midi (MidiOutput, threading.Thread):
    """ class Midi 

    Evaluierung als callback ausführen 
    """

    paused = False
    pause_cond = threading.Condition (threading.Lock ())

    # Create the USBMonitor instance, watch for plugin USB devices:
    monitor = USBMonitor()

    def __init__ (self):
        threading.Thread.__init__ (self, target=self.run)
        MidiOutput.__init__ (self)

        self.daemon = True

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
                    port = self.in_ports[i].port
                    if port is not None:    
                        for msg in port.iter_pending ():
                            self.in_ports[i].eval_msg (msg)
            time.sleep (0.02)


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


    def clear_lists (self, group:str="all", lo:int=0, hi:int=1000):
        """ Listen der verwendeten Fader und Buttons leeren 

        group: 'all', 'fader' or 'button'
        """
        if group == "all":
            self.in_faders = [{} for i in range (4)] # verwendete Fader
            self.out_faders = [{} for i in range (4)] # verwendete Fader
            self.in_buttons = [{} for i in range (4)] # verwendete Buttons
            self.out_buttons = [{} for i in range (4)] # verwendete Buttons
        elif group == "button":
            for line in self.in_buttons:
                for key in line.copy():
                    if lo <= line[key] < hi:
                        del line[key]
            for line in self.out_buttons:
                for key in line.copy():
                    if lo <= line[key] < hi:
                        del line[key]
        elif group == "fader":
            for line in self.in_faders:
                for key in line.copy():
                    if lo <= line[key] < hi:
                        del line[key]
            for line in self.out_faders:
                for key in line.copy():
                    if lo <= line[key] < hi:
                        del line[key]



    def set_indevice (self, pos:int, num:int) ->dict:
        """ Midigerät zuweisen
        
        pos: Position in self.in_devices, 0 <= pos < 4
        num: Devicenummer neu oder ändern
        return: {"message":str, "category": "error" oder "success"}
        """
        ret = {}
        ret["category"] = "danger"
        if 0 <= pos < 4:
            newdev = self.in_ports[pos] # MidiDevice 
        else:
            ret["message"] = f"{pos} nicht gültig."
            self.logger.debug (f"Input Nummer {pos+1} nicht gültig.")
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
        
        self.logger.debug (f"Input {pos+1} : {ret['message']}")
        return ret


    def reconnect (self, *args):
        """ Midi Geräte neu verbinden

        Diese Testfunktion wird nur lokal verwendet. In Club-DMX wird die
        Funktion connect_midi () verwendet, siehe startup.py
        """
        # print (f"args: {args}")
        tmp_in_ids = []
        for dev in self.in_ports:
            tmp_in_ids.append (dev.device_id)
        # print (f"In IDs: {tmp_in_ids}")
        devices = self.list_devices (mode="input")

        for count, dev in enumerate (tmp_in_ids):
            if dev != -1:
                self.in_ports[count].clear ()
                self.in_ports[count].set_device (devices, dev)
                self.in_ports[count].index = count

        tmp_out_ids = []
        for dev in self.out_ports:
            tmp_out_ids.append (dev.device_id)
        # print (f"Out IDs: {tmp_out_ids}")
        devices = self.list_devices (mode="output")

        for count, dev in enumerate (tmp_out_ids):
            if dev != -1:
                self.out_ports[count].clear ()
                self.out_ports[count].set_device (devices, dev)
                self.out_ports[count].index = count
        

# --- Test -------------------------------------------------------------------
if __name__ == "__main__":

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
    # Start the daemon
    mididev.monitor.start_monitoring(on_connect= mididev.reconnect,
                                     on_disconnect=None)


    # midiout = MidiOutput ()
    print (infotxt)

    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            cmd = i.split ()
            if i == '#' or i == '':
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
            elif i == 'a':
                for dev in mididev.out_ports:
                    print (dev)
            elif i == 'r':
                mididev.reconnect ()
                

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



