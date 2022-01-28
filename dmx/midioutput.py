#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Klassen MidiDevice und MidiOutput """

import pygame
import pygame.midi
# from time  import sleep

import midi_devices as mdev

class MidiDevice ():
    """ Datensammlung zu einem Midi-Gerät """

    def __init__ (self):
        self.device_id = -1
        self.name = mdev.NO_MIDI_DEVICE
        # self.miditype = None # 'input' oder 'output'
        self.midi_device = None # das pygame.midi.Input bzw. Output Objekt
        # pygame wird hier in dieser Klasse nicht initialisiert
        self.buttons = [] # Kontrollerliste der Buttons am Gerät
        self.faders = []  # Kontrollerliste der Fader am Gerät
        # zur späteren Verwendung in Klasse Midi:
        # Liste der Midi-Fader timestamps:
        self.fader_buffer  = []
        self.fader_update  = []


    def __repr__(self):
        return "<MidiDevice {}, {}>".format (self.device_id, self.name)

    def clear (self):
        """ Mididevice rücksetzen """
        if self.midi_device:
            self.midi_device.close ()
            # self.midi_device.abort ()
        self.device_id = -1
        self.name = mdev.NO_MIDI_DEVICE
        self.midi_device = None
        self.buttons.clear ()
        self.faders.clear ()
        self.fader_buffer.clear ()
        self.fader_update.clear ()
        # self.miditype = None

    def set_device (self, devlist:list, num:int):
        """ Werte zuweisen 
        
        devlist: Liste mit Device-Daten
        num: Nummer in devlist
        """
        devnums = [dev[0] for dev in devlist]
        if num in devnums:
            index = devnums.index (num)
            if devlist[index][3] == "frei":             # 'frei' oder 'verwendet'
                self.device_id = devlist[index][0]      # int >= 0
                self.name = devlist[index][1]           # str
                miditype  = devlist[index][2]      # 'input' oder 'output'
                if miditype == "input":
                    self.midi_device = pygame.midi.Input (self.device_id)
                else:
                    self.midi_device = pygame.midi.Output (self.device_id)

                if self.name in mdev.midi_device_dict.keys():
                    self.buttons = mdev.midi_device_dict [self.name][1]
                    self.faders  = mdev.midi_device_dict [self.name][0]
                else:
                    self.buttons = mdev.default_buttons
                    self.faders  = mdev.default_faders

            return {"name":self.name, "status":devlist[index][3]} 
            # else:
            #     return devlist[index][3]
        else:
            return {"name":mdev.NO_MIDI_DEVICE, "status":""} 


class MidiOutput ():
    """ MIDI Output Klasse """

    def __init__ (self):
        # MidiDevice.__init__ (self)
        self.out_devices = [MidiDevice() for i in range (4)] # verwendete Geräte
        self.out_buttons = [[] for i in range (4)] # verwendete Buttons
        self.out_faders = [[] for i in range (4)] # verwendete Fader
        self.msg_function = print 

        pygame.init()
        pygame.midi.init()


    def set_msg_function (self, newfunc):
        """ messages umleiten """
        self.msg_function = newfunc

    def message (self, args):
        """ message ausgeben """
        self.msg_function (args)


    def list_devices (self, mode:str="all") ->list:
        """ Midi-Geräte auflisten 
        mode: all, input, output
        device-Struktur: (count:int, name:str, in_out:str, stat:str)
        """
        devs = []
        device_count = pygame.midi.get_count()
        for count in range (device_count):
            xy = pygame.midi.get_device_info(count)
            name = xy[1].decode()
            description = name +  f" ({count})"

            if xy[2] == 1: # input device
                in_out = "input"
                if xy[4] == 1:
                    stat = "verwendet"
                else:
                    try:
                        # inp = pygame.midi.Input(count) # nötig?
                        stat = "frei"
                    except:
                        stat = "verwendet"
                if mode == "all" or mode == "input":
                    devs.append ((count, name, in_out, stat, description))

            elif xy[3] == 1:
                in_out = "output"
                if xy[4] == 1:
                    stat = "verwendet"
                else:
                    stat = "frei"
                if mode == "all" or mode == "output":
                    devs.append ((count, name, in_out, stat, description))

            else:
                in_out = "?"
                stat = "?"
        # print ("Midi Devices:", devs)
        return devs


    def check_devicenum (self, num:int, devtype:str) :
        """ prüfen, ob num in devicelist ist
        
        num: int >= 0
        devtype: 'all', 'input' oder 'output'
        return: devicelist zu 'devtype' oder False
        """
        devlist = self.list_devices(devtype)
        devnums = [dev[0] for dev in devlist]
        if num in devnums:
            return devlist
        else:
            return False


    def clear (self, pos:int):
        """ self.out_devices[pos] zurücksetzen
        """
        if 0 <= pos < 4:
            self.out_devices[pos].clear ()
        else:
            return f"{pos} nicht gültig."


    def set_outdevice (self, pos:int, num:int) ->str:
        """ Midigerät zuweisen
        
        pos: Position in self.out_devices, 0 <= pos < 4
        num: Devicenummer neu oder ändern
        """
        if 0 <= pos < 4:
            newdev = self.out_devices[pos] # MidiDevice 
        else:
            return f"{pos} nicht gültig."

        if self.check_devicenum (num, "all"):
            # midi_device bereits zugewiesen:
            if newdev.device_id == num: # keine Änderung
                return {"keine Änderung."}

            if newdev.midi_device: # midi_device vorhanden
                newdev.clear ()

            devlist = self.check_devicenum (num, "output")
            if devlist:
                ret = newdev.set_device (devlist, num)
                
        else:
            self.clear (pos)
            ret = f"Kein Zuordnen von Midi-Output {num}"
        return ret


    def led_on (self, pos:int, lednum:int):
        """ Wert 127 an Midi Output schicken 
        
        pos: Position in self.out_devices, 0 <= pos < 4
        lednum: index in self.buttons
        """
        device = self.out_devices[pos]
        if not device.midi_device:
            return
        if isinstance (lednum, str):
            lednum = int (lednum)
        if 0 <= lednum < len (device.buttons):
            device.midi_device.write_short (0xb0, device.buttons[lednum], 127)

    def led_off (self, pos:int, lednum:int):
        """ Wert 0 an Midi Output schicken 
        
        pos: Position in self.out_devices, 0 <= pos < 4
        lednum: index in self.buttons
        """
        device = self.out_devices[pos]
        if not device.midi_device:
            return
        if isinstance (lednum, str):
            lednum = int (lednum)
        if 0 <= lednum < len (device.buttons):
            device.midi_device.write_short (0xb0, device.buttons[lednum], 0)


    def level (self, pos:int, num:int, lev:int):
        """ Level an Fader-Monitor schicken 
        """
        device = self.out_devices[pos]
        if not device.midi_device:
            return
        if isinstance (num, str):
            num = int (num)
        if 0 < num <= len (device.faders):
            device.midi_device.write_short (0xb0, device.faders[num], lev)

    
# --- Test -------------------------------------------------------------------
if __name__ == "__main__":

    infotxt = """
---- MIDI Output Test -----

Kommandos: x = Exit
           # = zeige diese Info 

           a = zeige alle MIDI-Geräte
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
                for dev in mididev.out_devices:
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
