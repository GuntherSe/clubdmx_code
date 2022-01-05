#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Klassen MidiDevice und MidiOutput """

import pygame
import pygame.midi
# import time

import midi_devices as mdev

class MidiDevice ():
    def __init__ (self):
        # defaults:
        self.device_id = -1
        self.name = mdev.NO_MIDI_DEVICE
        self.miditype = None # 'input' oder 'output'
        # das pygame.midi.Input bzw. Output Objekt:
        self.midi_device = None

        self.msg_function = print 

        pygame.init()
        pygame.midi.init()


    def __del__ (self):
        if self.midi_device:
            del self.midi_device


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
                    devs.append ((count, name, in_out, stat))

            elif xy[3] == 1:
                in_out = "output"
                if xy[4] == 1:
                    stat = "verwendet"
                else:
                    stat = "frei"
                if mode == "all" or mode == "output":
                    devs.append ((count, name, in_out, stat))

            else:
                in_out = "?"
                stat = "?"
        # print ("Midi Devices:", devs)
        return devs


    def set_device (self, num:int) ->str:
        """ midi-Objekt über midi-Nummer zuweisen 
        """
        devlist = self.list_devices("all")
        devnums = [dev[0] for dev in devlist]

        # midi_device bereits zugewiesen:
        if self.device_id == num: # keine Änderung
            return {"name":self.name, "status":"verwendet"}

        if self.midi_device: # midi_device ändern
            self.midi_device.close ()
            # del self.midi_device
            self.midi_device = None
            self.name = mdev.NO_MIDI_DEVICE
            self.device_id = -1
            self.miditype = None

        if num in devnums:
            index = devnums.index (num)
            if devlist[index][3] == "frei":             # 'frei' oder 'verwendet'
                self.device_id = devlist[index][0]      # int >= 0
                self.name = devlist[index][1]           # str
                self.miditype  = devlist[index][2]      # 'input' oder 'output'
                if self.miditype == "input":
                    self.midi_device = pygame.midi.Input (self.device_id)
                else:
                    self.midi_device = pygame.midi.Output (self.device_id)
            return {"name":self.name, "status":devlist[index][3]} 
            # else:
            #     return devlist[index][3]
        else:
            return {"name":mdev.NO_MIDI_DEVICE, "status":""} 

class MidiOutput (MidiDevice):
    """ MIDI Output Klasse """

    def __init__ (self):
        MidiDevice.__init__ (self)
        # Dict der buttons und fader
        # key = controller, val = Button-Nummer
        self.buttons = {} 
        self.faders = {}  

    def __del__ (self):
        try:
            MidiDevice.__del__ (self)
        except:
            pass


    def set_device (self, num:int) ->str:
        devlist = self.list_devices("output")
        devnums = [dev[0] for dev in devlist]
        if num in devnums: # output Gerät
            ret = MidiDevice.set_device (self, num)
            if ret["status"] == "frei":
                if self.name in mdev.midi_device_dict:
                    self.buttons = mdev.midi_device_dict [self.name][1]
                    self.faders  = mdev.midi_device_dict [self.name][0]
                    # self.message (f"verwende {self.name}")
                else:
                    self.buttons = mdev.default_buttons
                    self.faders  = mdev.default_faders
                    # self.message (f"verwende {self.name} mit nanoKONTROL-2 Settings")
                
        else:
            ret = MidiDevice.set_device (self, -1)
        return ret

    def led_on (self, lednum:int):
        """ led Nr ab 0 """
        if not self.midi_device:
            return
        if isinstance (lednum, str):
            lednum = int (lednum)
        if lednum < 0 or lednum >= len (self.buttons):
            return
        # device = 0xb0 + self.device_id
        self.midi_device.write_short (0xb0, self.buttons[lednum], 127)

    def led_off (self, lednum:int):
        if not self.midi_device:
            return
        if isinstance (lednum, str):
            lednum = int (lednum)
        if lednum < 0 or lednum >= len (self.buttons):
            return
        # device = 0xb0 + self.device_id
        self.midi_device.write_short (0xb0, self.buttons[lednum], 0)

    def level (self, num:int, lev:int):
        """ Level an Fader-Monitor schicken 
        """
        if not self.midi_device:
            return
        if isinstance (num, str):
            num = int (num)
        if 0 < num <= len (self.faders):
            self.midi_device.write_short (0xb0, self.faders[num], lev)

    
# --- Test -------------------------------------------------------------------
if __name__ == "__main__":

    infotxt = """
---- MIDI Output Test -----

Kommandos: x = Exit
           # = zeige diese Info 

           a = zeige alle MIDI-Geräte
           i = zeige alle MIDI-input-Geräte
           o = zeige alle MIDI-output-Geräte
           <num> = verwende MIDI Input <num>
           k = verwende kein MIDI
           c = LED on
           v = LED off
"""

    mididev = MidiOutput ()
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
            elif i[0] == 'c':
                try:
                    cmd, num = i.split ()
                except:
                    num = 0
                mididev.led_on (num)
            elif i[0] == 'v':
                try:
                    cmd, num = i.split ()
                except:
                    num = 0
                mididev.led_off (num)

            else:
                try:
                    num = int(i)
                except:
                    num = None
                ret = mididev.set_device (num)
                print (f"Verwende {ret}, {mididev.miditype}")

    finally:
        print ("exit...")
