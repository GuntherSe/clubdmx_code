#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Unit Test:     patch.py
# 
#    
import os
from patch import Patch

roompath = os.environ.get ("ROOMPATH")
if roompath:
    os.chdir (roompath)
print ("ich bin hier: ", os.getcwd())
patchname = os.environ.get ("PATCHFILE")

patch = Patch ()
patch.set_path (os.getcwd())
patch.open (patchname)
# unis = patch.get_unis ()
# if len (unis):
#     patch.set_unis (unis)
#else: universes = 1


infotxt = """
---- Lichtpult Patch Test -----

Kommandos: x = Exit
            # = zeige diese Info
            u = Anzahl der Universen
            m = Zeige Mix Universum
            s = Sichere Patchfile Änderungen
            n = Sichere Patchfile unter 'neupatch'
            o = Öffne Patchfile 'neu'
            r = Patchfile neu laden
            d = Zeige Patch-Dir und Head-Dir

            p = Zeige Patch   Dict
            l = Zeige Patch-Zeile
            h = Zeige Head    Dict
            j = Zeige Head    Liste
            v = Zeige Virtual Dict
            f = Zeige Patch Attribute
            a = Wert des Head-Attributes
            1 = Zeige Head-Attribute

            2 = get Head Index
            3 = Add Head
            4 = Remove Head
            5 = Test Head Dict
            6 = Test set_attribute(Intensity)
            7 = Test set_attribute(Red)
            8 = Test attribtype
            9 = zeige Head-Details
            10 = Test set_attribute (Switch) 
            c = Farbwerte des Heads
"""        
print (infotxt)
try:
    i = 1
    while i != 'x':
        i = input ("CMD: ")
#            if i == 'x': break
        if i == 'u':
            print (patch.universes())
        elif i == '#':
            print (infotxt)
        elif i == 'm':
            uni = input ("Universum: ")
            print (patch.show_mix(uni))
        elif i == 's':
            patch.save ()
        elif i == 'n':
            patch.save ("neupatch")
        elif i == 'o':
            patch.open ("neu")
        elif i == 'r':
            patch.reload()
        elif i == 'd':
            print ("Patch-Dir:")
            print (patch.dir())
            print ("Head-Dir:")
            print (patch.dir("head"))
        elif i == 'p':
            print (patch.pdict)
        elif i == "l":
            line = input ("Patch Zeile: ")
            print (patch.patch_line(int (line)))
        elif i == 'h':
            print (patch.hdict)
        elif i == "j":
            print (patch.headlist())
        elif i == 'v':
            print (patch.vdict)
        elif i == 'f':
            print (patch.pfields())
        elif i == 'a':
            hd = input ("Head Nr.: ")
            print (patch.attriblist (hd))
            att = input ("Attribut: ")
            print (patch.attribute (hd, att))
        elif i == '1':
            hd = input ("Head Nr.: ")
            heads = patch.get_headindex(hd)
            if heads:
                print (patch.headinfo (heads[0]))
        elif i == '2':
            # Test get_headindex:
            hd = input ("Head Nr.: ")
            print (patch.get_headindex (hd))
        elif i == '3':
            #test add_head:
            ret = patch.add_head ()
            if ret == -1:
                print ("Ungültige Parameter")
            else:
                print ("Head {} eingefügt".format (ret))
#                    print (patch.pdict)
        elif i == '4':
            #test remove_head()
            hd = input ("Head Index zum Entfernen: ")
            patch.remove_head (hd)
        elif i == '5':
            # Test hdict:
            print (patch.hdict["Dimmer"]["Intensity"])
            print (patch.hdict["Dimmer"]["Intensity"][0])
            print (patch.hdict["LEDrgb_v"]["Intensity"][0])
        elif i == '6':
            # Test set_attribute:
            hd  = input ("Head: ")
            val = input ("Intensity: ")
            patch.set_attribute (hd, "Intensity", val)
        elif i == '7':
            # Test set_attribute:
            hd  = input ("Head: ")
            val = input ("Red: ")
            patch.set_attribute (hd, "Red", val)    
        elif i == '8':
            hd = input ("Head Nr.: ")
            print (patch.attriblist (hd))
            att = input ("Attribut: ")
            print (patch.attribtype (hd, att))
        elif i == '9':
            hd = input ("Head Nr.: ")
            print (patch.headdetails (hd))
        elif i == '10':
            # Test set_attribute:
            print ("Head: 1")
            val = input ("Switch: ")
            patch.set_attribute ("1", "Switch", val)
        elif i == 'c':
            val = input ("Head: ")
            print (patch.color (val))
        else:
            pass
finally:
    print ("exit...")





            
