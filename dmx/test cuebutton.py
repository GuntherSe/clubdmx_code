#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Modul-Test : cuebutton.py """

import os
import os.path
import time
import csv
# import pprint # pretty print

from cue import Cue
from cuebutton import Cuebutton
from patch import Patch
from ola import OscOla
from roombaseclass import Roombase

room = Roombase ("C:\\Users\\Gunther\\OneDrive\\Programmierung\\clubdmx_rooms\\test")

patch = Patch()
patch.set_path (room.path())
patch.open ("LED stripe")
patch.set_universes (2)
ola   = OscOla ()
ola.set_ola_ip ("192.168.0.11")
print("Verbinde zu OLA-device: {0}".format (ola.ola_ip))
ola.start_mixing()

Cue.set_path (room.path())

cue1 = Cuebutton (patch)
cue1.open ("led stripe red")
cue1.type = "Auswahl"
cue1.group = 1

cue2 = Cuebutton (patch)
cue2.open ("led stripe blue")
cue2.type = "Auswahl"
cue2.group = 1

cue3 = Cuebutton (patch)
cue3.open ("led stripe amber")
cue3.type = "Auswahl"
cue3.group = 1

cue4 = Cuebutton (patch)
cue4.open ("led stripe weiss_button")
cue4.type = "Auswahl"
cue4.group = 1
cue4.fade_out = 0
cue4.fade_in = 0

infotxt = """
---- Cuebutton Test -----

Kommandos: x = Exit
           # = zeige diese Info 

           c = Zeige Cuelist 1
           m = Zeige Mix Universum 1
           f = Zeige Cue File Name

           1 = Cue-1 GO
           2 = Cue-2 GO
           3 = Cue-3 GO
           4 = Cue-4 GO
           
"""

print (infotxt)
try:
    i = 1
    while i != 'x':
        i = input ("CMD: ")
        if i == '#':
            print (infotxt)
        elif i == 'c':
            print (cue1.cuelist())
        elif i == 'm':
            uni = 1 # input ("Universum: ")
            print (patch.show_mix(uni))
        elif i == 'f':
            print ("Cuebutton-1: {}".format (cue1.file.name())) 
            print ("Cuebutton-2: {}".format (cue2.file.name())) 
            print ("Cuebutton-3: {}".format (cue3.file.name())) 
            print ("Cuebutton-4: {}".format (cue4.file.name())) 
            
        elif i == '1':
            ret = cue1.go ()
            status = f"Status: {cue1.status} {cue2.status} {cue3.status} {cue4.status}"
            print (status)
        elif i == '2':
            ret = cue2.go ()
            status = f"Status: {cue1.status} {cue2.status} {cue3.status} {cue4.status}"
            print (status)
        elif i == '3':
            ret = cue3.go ()
            status = f"Status: {cue1.status} {cue2.status} {cue3.status} {cue4.status}"
            print (status)
        elif i == '4':
            ret = cue4.go ()
            status = f"Status: {cue1.status} {cue2.status} {cue3.status} {cue4.status}"
            print (status)

        else:
            pass
finally:
    print ("bye...")
