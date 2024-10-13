#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
Globale Objekte

Die folgenden Sessionvariablen werden verwendet:
selected_fadertable     basic_views
selected_buttontable    basic_views
selected_cuelist
editmode                
docpage
bootstraptheme
csvclipboard
stagename               stage
headstring              stage
singleheadindex         stage
visible + <datapath>    csv_views, data_views, room_views
datatab                 dataform
UPLOADPATH              fileupload
history
nexturl
retry_the_form          forms, formutils, patchform
modalactive             forms
usbdrive                forms, room_views
usbcheck                forms, room_views
deletefile              data_views, log_views
logname                 log_views

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
from startup      import connect_midi

# Daten-Verzeichnisstruktur:
# Das Verzeichnis, in dem sich globs.py befindet, ist der thispath
thispath  = os.path.dirname(os.path.realpath(__file__))
# aktuell: /clubdmx_code/app

# eine Ebene darüber:
basedir = os.path.dirname(thispath)
# aktuell: /clubdmx_code

ALLOWED_EXTENSIONS = set(['txt', 'csv', 'ccsv', 'zip', 'db'])
SHIFT = 1000 # für Fadertabellen zur Untrscheidung, siehe startup_func.py

# Globale Objekte:
cfgbase         = Config (os.path.join(basedir, ".app"))  
# zuletzt verwendete Config und Raum sind hier zu finden
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
    from oscinput import OscInput
    from apputils import evaluate_osc

    midiactive = False   
    midi = Midi ()
    # Start the daemon to detect Midi connections
    midi.monitor.start_monitoring(on_connect= connect_midi,
                                     on_disconnect=None)


    oscinput = OscInput ()
    oscinput.set_eval_function (evaluate_osc)