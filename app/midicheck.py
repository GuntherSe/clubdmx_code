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

# from csvfileclass import Csvfile
from midiutils import midi_commanddict


def midi_controller_list () ->list:
    """ deliver list of used Midi controllers 
    """
    if globs.PYTHONANYWHERE == "true":
        return []
    else:
        controller_list = []
        # Midi Input Buttons:
        for cnt, port in enumerate (globs.midi.in_buttons):
            for line in port:
                index = globs.midi.in_buttons[cnt][line]
                if index < globs.SHIFT:
                    controller_list.append ({"Midiinput":1+cnt,
                            "Controller":line+1,
                            "Type":"Button",
                            "Text":globs.buttontable[index].text,
                            "Parameter":globs.buttontable[index].location
                                         })
                else: # Midicommand 
                    key = str(cnt) + '-' + str(line)
                    controller_list.append ({"Midiinput":1+cnt,
                            "Controller":line+1,
                            "Type":"Command-Button",
                            "Text":midi_commanddict[key]["Command"],
                            "Parameter":midi_commanddict[key]["Parameter"]
                                         })
        # Midi Input Faders:
        for cnt, port in enumerate (globs.midi.in_faders):
            for line in port:
                index = globs.midi.in_faders[cnt][line]
                if index < globs.SHIFT:
                    controller_list.append ({"Midiinput":1+cnt,
                            "Controller":line+1,
                            "Type":"Fader",
                            "Text":globs.fadertable[index].text
                                        })
                else: # Cuelist
                    controller_list.append ({"Midiinput":1+cnt,
                            "Controller":line+1,
                            "Type":"Cuelist-Fader",
                            "Text":globs.cltable[index-globs.SHIFT].text
                                        })
        # Midi Output Buttons:
        for cnt, port in enumerate (globs.midi.out_buttons):
            for line in port:
                index = globs.midi.out_buttons[cnt][line]
                if index < globs.SHIFT:
                    controller_list.append ({"Midioutput":1+cnt,
                            "Controller":line+1,
                            "Type":"Button",
                            "Text":globs.buttontable[index].text,
                            "Parameter":globs.buttontable[index].location
                                         })
                else:
                    key = str(cnt) + '-' + str(line)
                    controller_list.append ({"Midioutput":1+cnt,
                            "Controller":line+1,
                            "Type":"Command-Button",
                            "Text":midi_commanddict[key]["Command"],
                            "Parameter":midi_commanddict[key]["Parameter"]
                                         })

        # Midi Output Faders:
        for cnt, port in enumerate (globs.midi.out_faders):
            for line in port:
                index = globs.midi.out_faders[cnt][line]
                if index < globs.SHIFT:
                    controller_list.append ({"Midioutput":1+cnt,
                            "Controller":line+1,
                            "Type":"Fader",
                            "Text":globs.fadertable[index].text
                                        })
                else: # Cuelist
                    controller_list.append ({"Midioutput":1+cnt,
                            "Controller":line+1,
                            "Type":"Cuelist-Fader",
                            "Text":globs.cltable[index-globs.SHIFT].text
                                        })

        # print (f"controller_list hat {len(controller_list)} Elemente.")
        return controller_list

