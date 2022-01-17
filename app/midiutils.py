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
                "CuelistPlus", "CuelistMinus"]
# Sammlung der Infos zu Midi-Commands abseits von den Commands, die in den
# Cues eingetragen sind.
# Ist der Inhalt der Tabelle als Dict
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
    num_devices = len (globs.midi.in_devices)
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
    
    controller: Midi-Controller Nummer ab 0
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
                        midibutton_monitor (count, 0)
            midibutton_monitor (index, ret)
    return ret


# --- MIDI Funktionen ---
# nur importieren, wenn PYTHONANYWHERE == "false"
def eval_midiinput (*data):
    """ midicontroller an requests schicken
    wird als output-Funktion für Midicontroller verwendet
    in Midicontroller.poll: self.output (index, type, cnt, self.fader_buffer[cnt
    data[0]: Geräte-Nummer
    data[1]: "fader" oder "button"
    data[2]: controller-Nummer ab 0
    data[3]: Wert in 0 .. 127
    """
    if not len (globs.fadertable): # beim Neu-Laden von config möglich
        return
    # index:int=data[0], type:str=data[1], fader:int=data[2], level:int=data[3]
    if data[1]=="fader" and data[2] in globs.midi.in_faders[data[0]]:
        fader =  globs.midi.in_faders[data[0]][data[2]]
        if fader < globs.SHIFT: # cuefader
            globs.fadertable[fader].level = data[3] / 127
            midifader_monitor ("cuefader", fader ,data[3])
        elif globs.SHIFT <= fader < 2*globs.SHIFT: # level von cueist
            globs.cltable[fader-globs.SHIFT].level = data[3] / 127
            midifader_monitor ("cuelist", fader-globs.SHIFT ,data[3])
        else: # Zusatz
            print (f"Special Midifader: {data[2]}, {data[3]}")
    elif data[1]=="button" and data[2] in globs.midi.in_buttons[data[0]]:
        index = globs.midi.in_buttons[data[0]][data[2]]
        if index < globs.SHIFT: #cuebutton
            if data[3]: # nur 'drücken' auswerten, nicht 'loslassen'
                press_cuebutton (index)
            else: # nur relevant, wenn Buttontype == Taster
                # dann auch Loslassen auswerten
                if index in range (len (globs.buttontable)):
                    buttontype = globs.buttontable[index].type
                    if buttontype == "Taster":
                        press_cuebutton (index)
        # keine Werte zwischen SHIFT und 2*SHIFT
        else: # Zusatz
            print (f"Special Midibutton: {data[2]}, {data[3]}")
            eval_midicommand (data[0], data[2], data[3])



def midibutton_monitor (index:int, status:int):
    """ Button-Status per LED am midioutput anzeigen 

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
            if ctrl:
                key = str(incnr-1) + '-' + str(ctrl-1)
                midi_commanddict[key] = content[count]
            # Midi-Input:
            if incnr and ctrl:
                if ctype == "Button":
                    globs.midi.in_buttons[incnr-1][ctrl-1] = count + 2*globs.SHIFT
                else:
                    globs.midi.in_faders[incnr-1][ctrl-1] = count + 2*globs.SHIFT
            # Midi-Output:
            if outcnr and ctrl:
                if ctype == "Button":
                    globs.midi.out_buttons[outcnr-1].append (ctrl-1)
                else:    
                    globs.midi.out_faders[outcnr-1].append (ctrl-1)


def eval_midicommand (device:int, ctrl:int, val:int):
    """ Midi-Input aus den Zusatz-Kommands auswerten
    
    device: Geräte-Nummer ab 0
    ctrl: Controller-Nummer ab 0
    val: Controller-Wert, 0 <= val <= 127. Nur Drücken auswerten, 
         Loslassen nicht auswerten
    """
    key = str(device) + '-' + str(ctrl)
    if key in midi_commanddict:
        line = midi_commanddict[key]
        if len (line["Parameter"]):
            params = line["Parameter"].split()
            index = int(params[0]) - 1
        else:
            index = -1
        if line["Command"] == "TopcueClear" and val:
            globs.topcue.clear ()
        elif line["Command"] == "CuelistGo" and val:
            if index in range (len (globs.cltable)):
                globs.cltable[index].go ()
        elif line["Command"] == "CuelistPause" and val:
            if index in range (len (globs.cltable)):
                globs.cltable[index].pause ()
        elif line["Command"] == "CuelistPlus" and val:
            if index in range (len (globs.cltable)):
                globs.cltable[index].increment_nextprep ()
        elif line["Command"] == "CuelistMinus" and val:
            if index in range (len (globs.cltable)):
                globs.cltable[index].decrement_nextprep ()
