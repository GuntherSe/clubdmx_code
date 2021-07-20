#!/usr/bin/env python
""" class MidiController:
MIDI Input
Korg Nano Kontrol Anbindung.

Midi anzeigen:
* Input devices einlesen
* in Listbox ausgeben
* Auswahl treffen, evtl mit Angabe der Fadertabelle

Auswahl der Fader-/Button-Dictionaries:
Device-Name in midi_device_dict nachschlagen. Dort sollen die passenden
Dictionaries / Listen zugeordnet werden.

"""

import pygame
import pygame.midi
import threading
import time

import midi_devices as mdev

# https://stackoverflow.com/questions/33640283/thread-that-i-can-pause-and-resume

class MidiController (threading.Thread):
    """ als thread ausführen: self.queue enthält die midi-Commands
    wird dann in app verarbeitet
    """
    def __init__ (self, device:str="", index:int=0):
        threading.Thread.__init__ (self, target=self.run)
        self.paused = False
        self.pause_cond = threading.Condition (threading.Lock ())
        self.setDaemon (True)

        # defaults:
        self.device_id = -1
        self.device_name = mdev.NO_MIDI_DEVICE

        pygame.init()
        pygame.midi.init()
        # das pygame.midi.Input Objekt:
        self.midi_input = None

        # Dictionary aller Input-Devices:
        # self.midi_input_devices = {} 
        
        #  umleiten für Ausgabe in message:
        self.msg_function = print 
        # Output:
        self.index  = index # für die Output-Funktion als Erkennung
        self.output = print

        # device_id, device_name, midi_faders und midi_buttons festlegen:
        self.midi_faders = {}
        self.midi_buttons = {}
        # Liste der Midi-Fader timestamps:
        self.fader_buffer  = [] # [0 for i in range (mdev.MAXFADERS)] 
        self.fader_update  = [] # [0 for i in range (mdev.MAXFADERS)] 

        self.set_input_device (device)

        # Thread starten:
        self.start ()


    def run (self):
        """ thread starten 
        """
        while True:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait ()

                self.receive_midi ()
            time.sleep (0.02)

    
    def pause (self):
        """ pausiere self.thread
        """
        self.paused = True
        self.pause_cond.acquire ()

    def resume (self):
        """ Pausenende self.thread
        """
        self.paused = False
        self.pause_cond.notify ()
        self.pause_cond.release ()


    def device_list (self, mode:str="all") ->list:
        """ Midi-Geräte auflisten 
        mode: all, input, output
        device-Struktur: (count:int, name:str, in_out:str, stat:str)
        """
        # pygame.midi.quit ()
        pygame.midi.init ()

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
                        inp = pygame.midi.Input(count)
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

            # devs.append ((1+count, name, in_out, stat))
        return devs


    def device_name (self, num:"int oder str") ->str:
        """ Namen-String zu Device-Nummer
        """
        if isinstance (num, str):
            nun = int(num)
        devicelist = self.device_list ()
        for device in devicelist:
            if device[0] == num:
                return device[1]
        # nicht gefunden:
        return ""
    
    
    def set_input_device(self, dev_name:str = None):
        """ Input Gerät festlegen 
        wenn dev_name: 
            in midiinputs suchen.
            Verfügbarkeit prüfen
        """
        if dev_name:
            port_ok = 0
            midiinputs = self.device_list ("input")
            for i in midiinputs:
                if i[1] == dev_name: # dev_name gefunden
                    if dev_name == self.device_name:
                        port_ok = 1
                    elif i[3] == "frei" :
                        # noch nicht in Verwendung oder mit gleichem 
                        # dev_name wieder aufgerufen
                        self.device_id = i[0]
                        port_ok = 2
                    else: 
                        msg = f"{dev_name} von anderem Programm verwendet."
                        self.message (msg)

            if port_ok:
                self.device_name = dev_name
                if dev_name in mdev.midi_device_dict:
                    self.midi_faders  = mdev.midi_device_dict [dev_name][0]
                    self.midi_buttons = mdev.midi_device_dict [dev_name][1]
                    self.message (f"verwende {dev_name}")
                else:
                    self.midi_faders  = mdev.Kontrol2_faders
                    self.midi_buttons = mdev.Kontrol2_buttons
                    self.message (f"verwende {dev_name} mit nanoKONTROL-2 Settings")

            if port_ok == 2: # neues Device
                fadercount = len (self.midi_faders)
                self.fader_buffer = [0 for i in range (fadercount)]
                self.fader_update = [0 for i in range (fadercount)]
                # self.midi_input nur dann zuweisen, wenn device_id != -1
                self.midi_input = pygame.midi.Input(self.device_id)
        
        else: # kein Midi
            self.midi_input    = None
            self.midi_faders   = {}
            self.midi_buttons  = {}
            self.fader_buffer  = [] 
            self.fader_update  = [] 


    def set_input (self, num:int):
        """ device_name über midi-Nummer zuweisen 
        """
        devlist = self.device_list("input")
        inputnums = [dev[0] for dev in devlist]
        if num in inputnums:
            index = inputnums.index (num)
            self.set_input_device (devlist[index][1])
        else:
            self.set_input_device (None)


    # def device_info(self):
    #     """ alle devices 
    #     https://github.com/atizo/pygame/blob/master/examples/midi.py
    #     """
    #     ret = ""
    #     midiinputs = self.device_list ("input")
    #     for i in midiinputs:
    #         ret += f"<p>{i[1]}, {i[3]}</p>"

    #     return ret


    def receive_midi(self):
        """ midi-input an den Output schicken
        Output: print oder andere Output-Funktion
        """

        if self.midi_input and self.device_id != -1:
            if self.midi_input.poll():
                msg = self.midi_input.read(100) # mehrere messages einlesen, sonst träge
                msglen = len(msg) # anzahl midi-messages
                for cnt in range (msglen):
                    controller = msg[cnt][0][1]
                    value = msg[cnt][0][2]
                    if controller in self.midi_faders: # fader gefunden
                        fader = self.midi_faders[controller]
                        if value != self.fader_buffer[fader]:
                            self.fader_buffer[fader] = value
                            self.fader_update[fader] = 1
                    elif controller in self.midi_buttons: # button
                        button = self.midi_buttons.index(controller)
                        self.output (self.index, "button", button, value)
                        # print (button, value)
                    else:
                        print ("NanoKontrol: Szene 1 aktiv?")
                for cnt in range (len(self.fader_update)):
                    if self.fader_update[cnt] == 1:
                        self.fader_update[cnt] = 0
                        self.output (self.index, "fader", cnt, self.fader_buffer[cnt])


    def set_msg_function (self, newfunc):
        """ messages umleiten """
        self.msg_function = newfunc

    def message (self, args):
        """ message ausgeben """
        self.msg_function (args)

    def set_output_function (self, newfunc):
        """ Output umleiten """
        self.output = newfunc


# --- Test -------------------------------------------------------------------
if __name__ == "__main__":

    infotxt = """
---- MIDI Test -----

Kommandos: x = Exit
           # = zeige diese Info 

           s = starte MIDI-input
           q = stop MIDI-input
           a = zeige alle MIDI-Geräte
           i = zeige alle MIDI-input-Geräte
           o = zeige alle MIDI-output-Geräte
           <num> = verwende MIDI Input <num>
           k = verwende kein MIDI
"""

    midicontrol = MidiController ()
    midicontrol.set_input_device ("nanoKONTROL")

    print (infotxt)

    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
            elif i == 's':
                midicontrol.resume ()
            elif i == 'q':
                midicontrol.pause ()
            elif i == 'a':
                ret = midicontrol.device_list ()
                for item in ret:
                    print (item)
            elif i == 'i':
                ret = midicontrol.device_list ("input")
                for item in ret:
                    print (item)
            elif i == 'o':
                ret = midicontrol.device_list ("output")
                for item in ret:
                    print (item)
            # elif i == 'n':
            #     midicontrol.set_input_device ("nanoKONTROL")
            # elif i == 't':
            #     midicontrol.set_input_device ("TaHorng Musical Instrument")
            elif i == 'k':
                midicontrol.set_input_device ()
            else:
                try:
                    num = int(i)
                except:
                    num = None
                midicontrol.set_input (num)

    finally:
        print ("exit...")




