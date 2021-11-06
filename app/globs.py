#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
Globale Objekte
"""

import os
import os.path

from configclass  import Config
from ola          import OscOla
from patch        import Patch
from cue          import Cue
from cuebutton    import Cuebutton
from cuelist      import Cuelist
from cuechild     import Topcue
from roomclass    import Room

# Daten-Verzeichnisstruktur:
# Das Verzeichnis, in dem sich globs.py befindet, ist der thispath
thispath  = os.path.dirname(os.path.realpath(__file__))
# aktuell: /clubdmx_code/app

# eine Ebene darüber:
basedir = os.path.dirname(thispath)
# aktuell: /clubdmx_code

ALLOWED_EXTENSIONS = set(['txt', 'csv', 'ccsv', 'zip'])


# Globale Objekte:
cfgbase         = Config (os.path.join(basedir, ".app"))  
# zuletzt verwendete Config und Raum sind hier zu finden
# current_room    = ""
room            = Room ()
cfg             = Config ()       # Config
patch           = Patch()
ola             = OscOla ()
topcue          = Topcue(patch)   # entspricht Programmer
fadertable      = []              # Liste der Cues für cuefader
buttontable     = Cuebutton.instances #  Liste der Buttons
cltable         = Cuelist.instances # Liste der Cuelisten

if os.environ.get ("PYTHONANYWHERE")  == "true":
    PYTHONANYWHERE  = "true"
else:
    PYTHONANYWHERE  = "false"

# --- MIDI und OSC-Input ----------------------------------------------------

if PYTHONANYWHERE == "false":
    from midiinput import MidiInput
    from midioutput import MidiOutput
    from oscinput import OscInput
    from apputils import evaluate_midi, evaluate_osc


    midiactive      = False   

    # Liste der zugeordneten Midi-Controller:
    midiin = [MidiInput (index=i) for i in range (4)]  
    # die von den Controllern zu beschickenden Empfänger.
    # nur diese Midi-Aktionen werden weiterverarbeitet:
    midifaderlist    = [{} for i in range (4)]              
    midibuttonlist   = [{} for i in range (4)]         

    midiout = MidiOutput ()  
    midiout_table = {}

    for i in range (4):
        midiin[i].set_eval_function (evaluate_midi)

    oscinput = OscInput ()
    oscinput.set_eval_function (evaluate_osc)