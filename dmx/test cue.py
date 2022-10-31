#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Modul-Test : cue.py """

import os
import os.path
import time
import csv
import pprint # pretty print

from cue import Cue
from patch import Patch
from ola import OscOla

os.chdir ("C:\\Users\\Gunther\\OneDrive\\Programmierung\\clubdmx_rooms\\develop")
print ("ich bin hier: ", os.getcwd())
patch = Patch()
patch.set_path (os.getcwd())
patch.open ("LED stripe")
ola   = OscOla ()
ola.set_ola_ip ("192.168.0.11")
print("Verbinde zu OLA-device: {0}".format (ola.ola_ip))
ola.start_mixing()

patch.set_universes (2)
Cue.set_path (os.getcwd())
cue1 = Cue (patch)
cue1.open ("led stripe red")
# cue1.level = 1.0
cue2 = Cue (patch)
cue2.open ("led stripe blue")
# cue2.level = 1.0

cuelist = [cue1, cue2]
pp = pprint.PrettyPrinter(depth=6)


infotxt = """
---- Lichtpult Cue Test -----

Kommandos: x = Exit
           # = zeige diese Info 

           c = Zeige Cuelist 1
           m = Zeige Mix Universum 1
           f = Zeige Cue File Name
           d = Cue 1 speichern
           s = Cue 1 in newcue.csv speichern
           
           a = Cue1 erweitern
           b = Cue1 ändern
           r = Zeile aus Cue1 entfernen

           1 = Add Cue 1
           2 = Add Cue 2
           3 = Zeige Att. von Head 13
           4 = Zeige contrib
           5 = Remove Cue 1
           6 = Remove Cue 2
           7 = Cue 1 Level HTP down
           8 = Cue 1 Level HTP up
           9 = zeige contrib Länge
"""

print (infotxt)
try:
    i = 1
    while i != 'x':
        i = input ("CMD: ")
        if i == '#':
            print (infotxt)
        elif i == 'c':
            print (cue1.cuecontent ())
        elif i == 'm':
            uni = 1 # input ("Universum: ")
            print (patch.show_mix(uni))
        elif i == 'f':
            print ("Cue1: {}".format (cue1.file.name())) 
            print ("Cue2: {}".format (cue2.file.name())) 
        elif i == 'd':
            cue1.save ()
        elif i == 's':
            cue1.save ("newcue")
        elif i == 'a':
            cue1.set_attribute ("14", "Red", "255")
            cue1.set_attribute ("14","Intensity","234")
        elif i == 'b':
            cue1.set_attribute ("13","Red","100")
        elif i == 'r':
            cue1.remove_attribute ("13","Red")
            
        elif i == '1':
            # cue1.add_cuemix ()
            cue1.level   = 1.0
        elif i == '2':
            # cue2.add_cuemix ()
            cue2.level   = 1.0
        elif i == '3':
            intens = patch.attribute ("13","Intensity")
            red    = patch.attribute ("13","Red")
            green  = patch.attribute ("13","Green")
            blue   = patch.attribute ("13","Blue")
            print (intens, red, green, blue)
        elif i == '4':
            #print (cue1.contrib.contrib())
            pp.pprint(Cue.contrib.contrib())
            print ()
        elif i == '5':
            cue1.rem_cuemix()
            # del cue1
        elif i == '6':
            cue2.rem_cuemix()
        elif i == '7':
            level = cue1.level
            level -= 0.05
            if level < 0:
                level = 0
            cue1.level = level
            # cue1.add_cuemix ()
        elif i == '8':
            level = cue1.level
            level += 0.05
            if level > 1:
                level = 1
            cue1.level = level
            # print ("cue1-level: ", cue1._level)
            # cue1.add_cuemix ()
        elif i == '9':
            print ("contrib: ", Cue.contrib.len())
        else:
            pass
finally:
    print ("bye...")
