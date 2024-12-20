#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
Midi Utilities:
- Midi Input auswerten
- Buttonstatus an Midioutput schicken
- Faderstatus an Midioutput schicken
"""

import globs

import os
import os.path

from flask  import session
from csvfileclass import Csvfile

# Strings zur Identifizierung der Midi-Kommandos:
midi_commandlist =  ["TopcueClear", "CuelistGo", "CuelistPause", 
                "CuelistPlus", "CuelistMinus", "CuelistBack"]
# Sammlung der Infos zu Midi-Commands abseits von den Commands, die in den
# diversen csv-Tabellen eingetragen sind: cuefader, cuebutton, cuelist-pages
# 
# Der Inhalt der Midibutton-Tabelle als Dict ist hier:
midi_commanddict = {}

def command_choices () ->list:
    """ choices-Liste aus Commands, die mit Midi-Buttons ausgelöst werden
    """
    ret = []
    for cmd in midi_commandlist:
        ret.append ((cmd,cmd))
    return ret


def check_midicontroller (incnt:str, outcnt:str, controller:str) ->list:
    """ csv-Einträge zu Midicontroller verifizieren
    
    incnt: Midi-Input Gerät (Geräte-Zählung ab 1)
    outcnt: Midi-Output Gerät (Geräte-Zählung ab 1)
    controller: Controller-Nummer, Zählung ab 1
    return: [incnt,outcnt,controller] 
        0 bedeutet ungültiger Wert
    """
    num_devices = len (globs.midi.in_ports)
    # Midiinput-Nummer, Zählung ab 1:
    try: 
        incnr = int (incnt)
        if not (1 <= incnr <= num_devices):
            incnr = 0
    except:
        incnr = 0
    # Midioutput-Nummer, Zählung ab 1:
    try: 
        outcnr = int (outcnt)
        if not (1 <= outcnr <= num_devices):
            outcnr = 0
    except:
        outcnr = 0
    # MidiFader-Nummer, Zählung ab 1:
    try: 
        fnr = int (controller)
    except:
        fnr = 0
    return [incnr,outcnr,fnr]


def press_cuebutton (index:int) -> int:
    """ cuebutton auf website oder midi drücken
    
    index: button-Nummer ab 0
           (das ist auch der index in globs.buttontable.instances)
    return: 1 = on, 0 = off
    """
    ret = 0
    buttons = len (globs.buttontable)
    if index in range (buttons):
        ret = globs.buttontable[index].go()
        if globs.PYTHONANYWHERE == "false" and globs.midiactive:
            buttontype = globs.buttontable[index].type
            buttongroup = globs.buttontable[index].group
            if buttontype == "Auswahl":
                for count in range (buttons):
                    item = globs.buttontable[count]
                    if item.type == "Auswahl" and item.group == buttongroup:
                        cuebutton_monitor (count, 0)
            cuebutton_monitor (index, ret)
    return ret


def press_pausebutton (index:int):
    """ Cuelist-Pausebutton auf website oder midi drücken
    
    index: Cuelist-Nummer ab 0
           (das ist auch der index in globs.cltable.instances)
    """
    buttons = len (globs.cltable)
    if index in range (buttons):
        globs.cltable[index].pause()
        if globs.PYTHONANYWHERE == "false" and globs.midiactive:
            pausebutton_monitor (index)


# --- MIDI Funktionen ---
# nur importieren, wenn PYTHONANYWHERE == "false"
def eval_midi (pos, msg):
    """ Midi Inputs auswerten 
    
    pos: Position in self.in_ports 0 <= pos < 4
    msg:   mido-Message
    """
    if not len (globs.fadertable): # beim Neu-Laden von config möglich
        return
    if msg.type == "control_change":
        # in_faders = globs.midi.in_faders[pos]
        if msg.control in globs.midi.in_ports[pos].faders: # Fader erkannt
            ctrlindex = globs.midi.in_ports[pos].faders.index (msg.control)
            if ctrlindex in globs.midi.in_faders[pos]:
                fader = globs.midi.in_faders[pos][ctrlindex]
                if fader < globs.SHIFT: # cuefader
                    globs.fadertable[fader].level = msg.value / 127
                    midifader_monitor ("cuefader", fader , msg.value)
                elif globs.SHIFT <= fader < 2*globs.SHIFT: # cuelist
                    globs.cltable[fader-globs.SHIFT].level = msg.value / 127
                    midifader_monitor ("cuelist", fader-globs.SHIFT ,msg.value)
                else: # Zusatz
                    pass
        elif msg.control in globs.midi.in_ports[pos].buttons: # Button erkannt
            ctrlindex = globs.midi.in_ports[pos].buttons.index (msg.control)
            if ctrlindex in globs.midi.in_buttons[pos]:
                button = globs.midi.in_buttons[pos][ctrlindex]

                if button < globs.SHIFT: #cuebutton
                    if msg.value: # nur 'drücken' auswerten, nicht 'loslassen'
                        press_cuebutton (button)
                    else: # nur relevant, wenn Buttontype == Taster
                        # dann auch Loslassen auswerten
                        if button in range (len (globs.buttontable)):
                            buttontype = globs.buttontable[button].type
                            if buttontype == "Taster":
                                press_cuebutton (button)
                # keine Werte zwischen SHIFT und 2*SHIFT
                else: # Zusatz-Buttons
                    # print (f"Special Midibutton: {data}")
                    eval_midicommand (pos, ctrlindex, msg.value)


def cuebutton_monitor (index:int, status:int):
    """ Button-Status per LED am Midioutput anzeigen 

    index: index in globs.buttontable
    status 0 oder 1
    """
    outnum = globs.buttontable[index].midioutput
    button = globs.buttontable[index].midicontroller
    if outnum != -1 and  button != -1 :
        if status: # status == 1
            globs.midi.led_on (outnum, button)
        else:
            globs.midi.led_off (outnum, button)


def midifader_monitor (table: str, index:int, level:int):
    """ Faderlevel an Midioutput senden 
    
    table: 'cuefader' oder 'cuelist'
    index: index in der betreffenden Tabelle
    level: Wert zwischen 0 und 127
    """
    if table == "cuefader":
        outnum = globs.fadertable[index].midioutput
        controller = globs.fadertable[index].midicontroller
    elif table == "cuelist":
        outnum = globs.cltable[index].midioutput
        controller = globs.cltable[index].midicontroller
    globs.midi.level (outnum, controller, level)


def get_midicommandlist ():
    """ Zusätzliche Midi-Commands einlesen
    
    Command-Zuordnungen kommen aus Tabelle, definiert in globs.midi_buttons
    """
    midi_commanddict.clear ()
    globs.midi.clear_lists ("button", lo=2*globs.SHIFT, hi=3*globs.SHIFT)
    if globs.PYTHONANYWHERE == "false":
        filename = globs.cfg.get ("midi_buttons")
        csvfile = Csvfile (os.path.join (globs.room.midibuttonpath(), filename))
        content = csvfile.to_dictlist ()
        fieldnames = csvfile.fieldnames()
        for count in range (len (content)):
            incnr = content[count]["Midiinput"]
            outcnr = content[count]["Midioutput"]
            ctrl = content[count]["Controller"]
            ctype = content[count]["Type"] # 'Button' oder 'Fader'
            incnr, outcnr, ctrl = check_midicontroller (incnr,outcnr,ctrl)
            # Eintrag in command-Dict:
            # if ctrl:
            #     key = str(incnr-1) + '-' + str(ctrl-1)
            #     midi_commanddict[key] = content[count]
            # Midi-Input:
            if incnr and ctrl:
                key = str(incnr-1) + '-' + str(ctrl-1)
                midi_commanddict[key] = content[count]
                if ctype == "Button":
                    globs.midi.in_buttons[incnr-1][ctrl-1] = count + 2*globs.SHIFT
                else:
                    globs.midi.in_faders[incnr-1][ctrl-1] = count + 2*globs.SHIFT
            # Midi-Output:
            if outcnr and ctrl:
                key = str(outcnr-1) + '-' + str(ctrl-1)
                midi_commanddict[key] = content[count]
                if ctype == "Button":
                    # globs.midi.out_buttons[outcnr-1].append (ctrl-1)
                    globs.midi.out_buttons[outcnr-1][ctrl-1] = count + 2*globs.SHIFT
                else:    
#                    globs.midi.out_faders[outcnr-1].append (ctrl-1)
                    globs.midi.out_faders[outcnr-1][ctrl-1] = count + 2*globs.SHIFT


def eval_midicommand (device:int, ctrl:int, val:int):
    """ Midi-Input aus den Zusatz-Kommands auswerten
    
    device: Geräte-Nummer ab 0
    ctrl: Controller-Nummer ab 0
    val: Controller-Wert, 0 <= val <= 127. Nur Drücken auswerten, 
         Loslassen nicht auswerten
    mit mido-Modul kein Debuggen möglich? 
    Leider mit mido.port.callback nicht, daher Midi-Input mit Thread
    """
    key = str(device) + '-' + str(ctrl)
    # print ("key: ", key, ", val: ", val)
    if key in midi_commanddict:
        line = midi_commanddict[key]
        if len (line["Parameter"]):
            params = line["Parameter"].split()
            index = int(params[0]) - 1
        else:
            index = -1
        if line["Command"] == "TopcueClear" and val:
            globs.topcue.clear ()
            # send val to midi output:
            outdevice = line["Midioutput"]
            if outdevice:
                out = int (outdevice)-1
                if 0 <= out < 4:
                    globs.midi.level (out, ctrl, val)
        elif line["Command"] == "CuelistGo" and val:
            if index in range (len (globs.cltable)):
                globs.cltable[index].go ()
                pausebutton_monitor (index)
        elif line["Command"] == "CuelistPause" and val:
            press_pausebutton (index)
            # if index in range (len (globs.cltable)):
            #     globs.cltable[index].pause ()
        elif line["Command"] == "CuelistPlus" and val:
            if index in range (len (globs.cltable)):
                globs.cltable[index].increment_nextprep ()
        elif line["Command"] == "CuelistMinus" and val:
            if index in range (len (globs.cltable)):
                globs.cltable[index].decrement_nextprep ()
        elif line["Command"] == "CuelistBack" and val:
            if index in range (len (globs.cltable)):
                globs.cltable[index].go ("-1")
                pausebutton_monitor (index)


def pausebutton_monitor (index:int):
    """ Pause-Status per LED am Midioutput anzeigen 

    index: Zeilennr in globs.cltable ab 0
    """
    if globs.cltable[index].is_paused:
        status = 1
    else:
        status = 0

    # print (f"CuelistNr: {index}, Status: {status}")
    # Midioutput und Controller finden:
    for key in midi_commanddict:
        line = midi_commanddict[key]
        if line["Command"] == "CuelistPause":
            params = line["Parameter"].split()
            if int(params[0]) - 1 == index:
                midiout = int(line["Midioutput"]) - 1
                controller = int(line["Controller"]) - 1

    if globs.PYTHONANYWHERE == "false":
        try:
            if status: # status == 1
                globs.midi.led_on (midiout, controller)
            else:
                globs.midi.led_off (midiout, controller)
        except: # error beim startup?
            pass