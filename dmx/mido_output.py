#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Klassen MidiDevice und MidiOutput """

import mido

import midi_devices as mdev

import logging
from loggingbase import Logbase

class MidiDevice ():
    """ Datensammlung zu einem Midi-Gerät """

    def __init__ (self):
        self.device_id = -1
        self.name = mdev.NO_MIDI_DEVICE
        # self.miditype = None # 'input' oder 'output'
        self.port = None # der mido Input bzw. Output Port
        self.buttons = [] # Kontrollerliste der Buttons am Gerät
        self.faders = []  # Kontrollerliste der Fader am Gerät
        # zur späteren Verwendung in Klasse Midi:
        self.index = -1 # Port-Nummer (0-3)
        self.eval = print   # Auswertung des Midi-Inputs


    def __repr__(self):
        return "<MidiDevice {}, {}>".format (self.device_id, self.name)


    def clear (self):
        """ Mididevice rücksetzen """
        if self.port:
            self.port.close ()
        self.device_id = -1
        self.name = mdev.NO_MIDI_DEVICE
        self.port = None
        self.index = -1
        self.buttons.clear ()
        self.faders.clear ()


    def set_device (self, devlist:list, count:int):
        """ Werte zuweisen 
        
        devlist: Liste mit Device-Daten, siehe MidiOutput:list_devices()
        count: erster Wert in Device-Daten
        Device-Daten: [(count, name, mode, description), ...]
        result: {"name":self.name, "result":"true" oder "false"}
        """
        devindex = -1
        for i, val in enumerate (devlist):
            if val[0] == count:
                devindex = i
                break

        if devindex in range (len (devlist)):
            miditype  = devlist[devindex][2]       # 'input' oder 'output'
            description = devlist[devindex][3]     # str
            try:
                if miditype == "input":
                    self.port = mido.open_input (description)
                else:
                    self.port = mido.open_output (description)
            except:
                return {"name":mdev.NO_MIDI_DEVICE, "result":"false"} 

            self.device_id = devindex  # int >= 0
            self.name = devlist[devindex][3]       # str

            for key in mdev.midi_device_dict.keys():
                if ':' in description: # Linux
                    split = description.split (sep=':')
                else: # Windows
                    split = description.split ()

                if key in split:
                    self.buttons = mdev.midi_device_dict [key][1]
                    self.faders  = mdev.midi_device_dict [key][0]
                    return {"name":self.name, "result":"true" } 

            self.buttons = mdev.default_buttons
            self.faders  = mdev.default_faders
            return {"name":self.name, "result":"true" } 

        else:
            return {"name":mdev.NO_MIDI_DEVICE, "result":"false"} 


    def set_eval_function (self, newfunc):
        """ neue eval-Funktion zuweisen 
        """
        self.eval = newfunc


    def eval_msg (self, msg):
        """ midi-input mittels eval weiterverarbeiten

        self.index an eval-Funktion übermitteln
        msg: mido Message
        eval: print oder andere eval-Funktion
        """
        self.eval (self.index, msg)
        return
    
class MidiOutput ():
    """ MIDI Output Klasse """

    # ein logger für Midi:
    baselogger = Logbase ()
    logger = logging.getLogger (__name__)
    file_handler = baselogger.filehandler ("midi.log")
    logger.addHandler (file_handler)


    def __init__ (self):
        self.out_ports = [MidiDevice() for i in range (4)] # verwendete Geräte
        self.out_buttons = [{} for i in range (4)] # verwendete Buttons
        self.out_faders = [{} for i in range (4)] # verwendete Fader
    #     self.msg_function = print 


    # def set_msg_function (self, newfunc):
    #     """ messages umleiten """
    #     self.msg_function = newfunc

    # def message (self, args):
    #     """ message ausgeben """
    #     self.msg_function (args)


    def list_devices (self, mode:str="input") ->list:
        """ Midi-Geräte auflisten 
        mode: input, output
        device-Struktur: (count:int, name:str, mode, description:str)
        name ist unterschiedlich in Win und Linux, daher müssen hier verschiedene
        Fälle berücksichtigt werden.
        z.B.: 'nanoKONTROL:nanoKONTROL MIDI 1 20:0' oder 'nanoKONTROL MIDI 1 0'
        """
        devs = [] # die fertige Liste
        appended = [] # zur Kontrolle, ob mehrfach eingefügt wird
        if mode == "input":
            devlist = mido.get_input_names ()
        elif mode == "output":
            devlist = mido.get_output_names ()
        else:
            return devs

        # devlist erzeugen:
        for count, dev in enumerate (devlist):
            if ':' in dev:
                split = dev.split (sep=':')
            else:
                split = dev.rpartition (' ')
            name = split[0] # zur Identifikation in mdev.device_list
            # dev: zur Identifikation in der Auswahl bei Config
            if dev not in appended:
                appended.append (dev)
                devs.append ((count, name, mode, dev ))

        return devs


    def clear (self, pos:int):
        """ self.out_ports[pos] zurücksetzen
        """
        if 0 <= pos < 4:
            self.out_ports[pos].clear ()
        else:
            return f"{pos} nicht gültig."


    def set_outdevice (self, pos:int, num:int) ->str:
        """ Midigerät zuweisen
        
        pos: Position in self.out_ports, 0 <= pos < 4
        num: Devicenummer neu oder ändern
        """
        ret = {}
        ret["category"] = "danger"
        if 0 <= pos < 4:
            newdev = self.out_ports[pos] # MidiDevice 
        else:
            ret["message"] = f"{pos} nicht gültig."
            return ret

        if newdev.device_id != -1: # midi_device vorhanden
            newdev.clear ()

        devlist = self.list_devices ("output")
        if devlist and num != -1: # input Gerät
            msg = newdev.set_device (devlist, num)
            if msg["result"] == "true":
                newdev.index = pos
                ret["message"] = msg["name"]
                ret["category"] = "success"
            else:
                self.clear (pos)
                ret["message"] = f"Midi-Output-Gerät {num} belegt"

        else:
            self.clear (pos)
            ret["message"] = f"Midi-Output-Gerät {num} nicht zugewiesen"

        self.logger.debug (f"Output {pos+1} : {ret['message']}")
        return ret


    def led_on (self, pos:int, lednum:int):
        """ Wert 127 an Midi Output schicken 
        
        pos: Position in self.out_ports, 0 <= pos < 4
        lednum: index in self.buttons
        """
        device = self.out_ports[pos]
        if not device.port:
            return
        if isinstance (lednum, str):
            lednum = int (lednum)
        
        if 0 <= lednum < len (device.buttons):
            msg = mido.Message ("control_change", 
                control=device.buttons[lednum], value=127)
            device.port.send (msg)
            # print ("led on")

    def led_off (self, pos:int, lednum:int):
        """ Wert 0 an Midi Output schicken 
        
        pos: Position in self.out_ports, 0 <= pos < 4
        lednum: index in self.buttons
        """
        device = self.out_ports[pos]
        if not device.port:
            return
        if isinstance (lednum, str):
            lednum = int (lednum)
        if 0 <= lednum < len (device.buttons):
            msg = mido.Message ("control_change", 
                control=device.buttons[lednum], value=0)
            device.port.send (msg)
            # print ("led off")


    def level (self, pos:int, num:int, lev:int):
        """ Level an Fader-Monitor schicken

        pos: Position in self.out_ports, 0 <= pos < 4
        num: Controller Nummer ab 0
        lev: Level 0 <= lev <= 127
        """
        device = self.out_ports[pos]
        if not device.port:
            return
        if isinstance (num, str):
            num = int (num)
        if 0 <= num < len (device.faders):
            msg = mido.Message ("control_change", 
                control=device.faders[num], value=lev)
            device.port.send (msg)
            # print ("level")

    
# --- Test -------------------------------------------------------------------
if __name__ == "__main__":

    infotxt = """
---- MIDI Output Test -----

Kommandos: x = Exit
           # = zeige diese Info 

           i = zeige alle MIDI-input-Geräte
           o = zeige alle MIDI-output-Geräte
           s = zeige verwendete Geräte
           <pos> <num> = verwende MIDI Output <num> an Gerät <pos>
           k <pos> = verwende kein MIDI an Gerät <pos>
           v <pos> <num> = LED <num> off an Gerät <pos>
           c <pos> <num> = LED <num> on an Gerät <pos>
"""

    mididev = MidiOutput ()
    # midiout = MidiOutput ()
    print (infotxt)

    try:
        i = "1"
        while i != 'x':
            i = input ("CMD: ")
            cmd = i.split ()
            if i == '#' or i == '':
                print (infotxt)
            elif i == 'i':
                ret = mididev.list_devices ("input")
                for item in ret:
                    print (item)
            elif i == 'o':
                ret = mididev.list_devices ("output")
                for item in ret:
                    print (item)
            elif i == 's':
                for dev in mididev.out_ports:
                    print (dev)

            elif cmd[0] == 'k':
                try:
                    ret = mididev.set_outdevice (int(cmd[1]), -1)
                except:
                    ret = mididev.set_outdevice (0, -1)
                print (ret)
            elif cmd[0] == 'c':
                try:
                    mididev.led_on (int(cmd[1]), cmd[2])
                except:
                    mididev.led_on (0,0)
            elif cmd[0] == 'v':
                try:
                    mididev.led_off (int(cmd[1]), cmd[2])
                except:
                    mididev.led_off (0,0)

            else:
                try:
                    ret = mididev.set_outdevice (int(cmd[0]), int(cmd[1]))
                    print (ret)
                except:
                    pass

    finally:
        print ("exit...")
