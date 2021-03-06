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
SHIFT = 1000 # für Fadertabellen zur Untrscheidung, siehe startup_func.py

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
    from mido_input import Midi
    # from midioutput import MidiOutput
    from oscinput import OscInput
    from apputils import evaluate_osc

    midiactive      = False   
    midi = Midi ()

    oscinput = OscInput ()
    oscinput.set_eval_function (evaluate_osc)