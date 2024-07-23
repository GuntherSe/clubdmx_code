#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
Midi Check Utilities:

Die Verwendung von Midi Buttons und Fadern ist in verschiedenen csv-Dateien
abgespeichert. Beim Startup bzw beim Wechseln von Config-Files werden diese
Infos eingelesen.

Midi-Fader werden verwendet in: cuefader, pages (= cuelist-pages).
Midi-Buttons werden verwendet in: cuebutton, midibutton

"""

import globs

import os
import os.path

from csvfileclass import Csvfile


def midi_controller_list () ->list:
    """ deliver list of used Midi controllers 
    """
    if globs.PYTHONANYWHERE == "true":
        return []
    else:
        controller_list = []
        for line in globs.midi.in_buttons:
            pass

        return controller_list

