#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
  Startup-Funktionen
"""
import globs

import os
import os.path
# import time

# from configclass  import Config
# from roomclass import Room
from cue import Cue
from cuebutton import Cuebutton
from cuelist import Cuelist
from csvfileclass import Csvfile
from startup_levels import backup_currentlevels, restore_currentlevels
from startup_levels import button_locations, fader_locations

def del_cuetables ():
    """ fadertable, buttontable, cltable löschen 
    Verwendet in load_config ()
    """

    for count in range (len(globs.fadertable)):
        globs.fadertable[count].rem_cuemix()
    globs.fadertable.clear ()
    for count in range (len(globs.buttontable)):
        globs.buttontable[count].rem_cuemix()
    globs.buttontable.clear ()
    for count in range (len(globs.cltable)):
        globs.cltable[count].outcue.rem_cuemix()
    globs.cltable.clear ()


def del_midilists ():
    """ globale midifaderlist und midibuttonlist leeren
    """
    if globs.PYTHONANYWHERE == "false":
        num_controllers = len (globs.midiin)
        globs.midifaderlist  = [{} for i in range (num_controllers)]
        globs.midibuttonlist = [{} for i in range (num_controllers)]    


def check_levelrequest (with_savedlevels:bool) ->bool:
    """ Prüfen, ob csv-Levels eingelesen werden sollen
    """
    if  with_savedlevels == True:
        savelevels = globs.cfg.get("savecuelevels") 
        if savelevels == "1":
            return True
    return False

def fadertable_items (location:str)   ->list:
    """ alle Cues aus der Fadertabelle mit location==location
    siehe Cuebutton.items
    """
    ret = []
    for inst in globs.fadertable:
        if inst.location == location:
            item = {}
            item["Text"] = inst.text
            item["Filename"] = inst.file.shortname()
            item["Index"] = globs.fadertable.index (inst)
            ret.append (item)
    return ret


# --- Fader-info ------------------------------------------------------

def make_fadertable (with_savedlevels:bool=False) :
    """ Liste mit Fader-Cues erzeugen

    location: entweder 'cuefaders' oder 'exefaders'
    fadertable:  globale Liste der Cue-Fader (aus exefader und cuefader)
    falls in config angegeben, dann Levels einlesen
    """
    currentlevels = backup_currentlevels ("fader") # aktuelle Level
    # Cue.contrib.pause ()

    locations = fader_locations
    new_fadertable = []
    # globs.fadertable.clear ()

    # für jeden Midicontroller ein dict mit den auszuwertenden
    # Midi-Aktionen anlegen:
    # davor wurde bereits midifaderlist geleert!
    if globs.PYTHONANYWHERE == "false":
        num_controllers = len (globs.midiin)
    #     globs.midifaderlist = [{} for i in range (num_controllers)]

    # sollen csv-gespeicherte Levels geladen werden?
    csvlevels_requested = check_levelrequest (with_savedlevels)
    fadernum = 0
    for loc in locations:
        filename = globs.cfg.get(loc)
        fullname = os.path.join (globs.room.cuefaderpath() , filename)
        csvfile = Csvfile (fullname)
        cuelist = csvfile.to_dictlist ()
        fieldnames = csvfile.fieldnames()
        try:
            fileindex = fieldnames.index ("Filename") 
        except:
            print (f"'Filename' nicht in {filename}")
            continue
        
        if csvlevels_requested: 
            try: # nur zur Fehler-Ausgabe
                levelindex = fieldnames.index ("Level")
            except:
                print (f"'Level' nicht in {filename}")


        for count in range (len (cuelist)):
            newcue = Cue (globs.patch)
            # globs.fadertable.append (newcue) # Konstruktor
            new_fadertable.append (newcue)
            fadernum = fadernum + 1 
            filename = cuelist[count]["Filename"]
            if filename == "":
                filename = "_neu"
            newcue.open (filename)
            newcue.location = loc
            newcue.id = loc + str (count)
            newcue.text = cuelist[count]["Text"]

            # nun Midi-Requests einlesen:
            if globs.PYTHONANYWHERE == "false":
                num_controllers = len (globs.midiin)
                try:
                    cnr = cuelist[count]["Midiinput"] # cnr:str ab 1 =ControllerNr
                    fnr = cuelist[count]["Midifader"] # fnr:str ab 1 =FaderNr
                    # print (f"Midi-Controller:{cnr}, Fader:{fnr}")
                except:
                    print ("Midi-Info nicht in cuefaders")
                    cnr = -1
                    fnr = -1
                # cnr und fnr können '' sein:
                if cnr and fnr:
                    cnr = int(cnr)-1
                    fnr = int(fnr)-1
                    if cnr in range(num_controllers):
                        controller = globs.midifaderlist[cnr]
                        controller[fnr] = fadernum - 1    #count
        
            # nun Levels:    
            if csvlevels_requested:        
                try:
                    level = float (cuelist[count]["Level"])
                except: # Default 0.0
                    level = 0.0
                newcue.level = level

    if with_savedlevels == False: # aktuelle Levels wiederherstellen
        restore_currentlevels (new_fadertable, currentlevels)
    globs.fadertable = new_fadertable
    # Cue.contrib.resume ()


# --- Cue-Buttons -------------------------------------------------------------
def make_cuebuttons (with_savedlevels:bool=False):
    """ Button-Liste erzeugen
    Die Liste ist  Cuebutton:instances
    Buttons finden sich in cuebutton.html, executer.html
    location: cuebuttons, exebuttons1, exebuttonx2
    with_savedlevels
        True: in File gespeicherte Levels laden, falls
              cfg.savecuelevels == 1
        False: aktuelle Levels wiederherstellen
    """
    currentlevels = backup_currentlevels ("button") # aktuelle Level
    # Cue.contrib.pause ()

    locations = button_locations
    # globs.buttontable.clear ()
    new_buttontable = []

    # midibuttonlist wurde bereits geleert
    # if globs.PYTHONANYWHERE == "false":
    #     num_controllers = len (globs.midiin)
    #     globs.midibuttonlist   = [{} for i in range (num_controllers)]    

    # sollen csv-gespeicherte Levels geladen werden?
    csvlevels_requested = check_levelrequest (with_savedlevels)
    butnum = 0    

    for loc in locations:
        filename = globs.cfg.get (loc)
        csvfile = Csvfile (os.path.join (globs.room.cuebuttonpath(), filename))
        cuelist = csvfile.to_dictlist ()
        fieldnames = csvfile.fieldnames()
        try: # nur zur Fehler-Ausgabe
            fileindex = fieldnames.index ("Filename") 
        except:
            print (f"Feld 'Filename' nicht in {filename}")
            continue
        
        if csvlevels_requested: 
            try: # nur zur Fehler-Ausgabe
                levelindex = fieldnames.index ("Level")
            except:
                print (f"Feld 'Level' nicht in {filename}")

        for count in range (len (cuelist)):
            newbut = Cuebutton(globs.patch) # Konstruktor
            new_buttontable.append (newbut)
            butnum = butnum + 1
            filename = cuelist[count]["Filename"]
            if filename == "":
                filename = "_neu"
            newbut.open (filename)
            newbut.location = loc
            newbut.id = loc + str (count)
            newbut.text = cuelist[count]["Text"]

            # Zeiten einlesen:
            newbut.fade_in = float (cuelist[count]["Fadein"])
            newbut.fade_out = float (cuelist[count]["Fadeout"])
            # Type (Schalter, Taster, Auswahl) und Group einlesen:
            newbut.type = cuelist[count]["Type"] 
            newbut.group = int (cuelist[count]["Group"])

            # nun Midi-Requests einlesen:
            if globs.PYTHONANYWHERE == "false":
                num_controllers = len (globs.midiin)
                try:
                    cnr = cuelist[count]["Midiinput"] # cnr:str ab 1 =ControllerNr
                    fnr = cuelist[count]["Midibutton"] # fnr:str ab 1 =FaderNr
                    # mon = cuelist[count]["Midibutton"] # MIDI-monitor
                    # print (f"Midi-Controller:{cnr}, Fader:{fnr}")
                except:
                    print ("Midi-Info nicht in cuebuttons")
                    cnr = -1
                    fnr = -1
                # cnr und fnr können '' sein:
                if cnr and fnr:
                    cnr = int(cnr)-1
                    fnr = int(fnr)-1
                    if cnr in range(num_controllers):
                        controller = globs.midibuttonlist[cnr]
                        controller[fnr] = butnum -1  #count
                else:
                    fnr = -1
                # MIDI-Monitor:
                try:
                    # TODO noch nicht implementiert, in layout anlegen
                    mon = cuelist[count]["Midimonitor"] # MIDI-monitor
                except:
                    # MIDI-monitor von button übernehmen
                    mon = fnr 
                if mon != -1:
                    globs.midiout_table[butnum-1] = mon

            # nun Levels:     
            if csvlevels_requested:
                try:
                    level = float (cuelist[count]["Level"])
                except: # Defaultwert eintragen
                    level = 0.0
                newbut.level = level
                # Buttonstatus:
                if level > 0:
                    newbut.status = 1
                else:
                    newbut.status = 0
               
    if with_savedlevels == False: # aktuelle Levels wiederherstellen
        restore_currentlevels (new_buttontable, currentlevels, type="button")

    # globs.buttontable.clear ()
    # Cuebutton.instances.clear ()
    Cuebutton.instances = new_buttontable
    globs.buttontable = new_buttontable
    # print ("done")
    # Cue.contrib.resume ()


# --- Cuelist-Tabelle erzeugen ------------------------------------------------

def make_cuelistpages (with_savedlevels:bool=False) :
    """ Liste mit Pages an Cuelisten erzeugen

    falls in config angegeben, dann Levels einlesen
    """
    new_cltable = []

    currentlevels = backup_currentlevels ("cuelist") # aktuelle Level
    # sollen csv-gespeicherte Levels geladen werden?
    csvlevels_requested = check_levelrequest (with_savedlevels)

    fadernum = 1000 # unterscheidet fader von cuefader
    filename = globs.cfg.get("pages")
    fullname = os.path.join (globs.room.pagespath() , filename)
    csvfile = Csvfile (fullname)
    pagelist = csvfile.to_dictlist ()
    fieldnames = csvfile.fieldnames()
    try: # Filename muss vorhanden sein
        fileindex = fieldnames.index ("Filename") 
    except:
        print (f"'Filename' nicht in {filename}")
        return
    
    if csvlevels_requested: 
        try: # nur zur Fehler-Ausgabe
            levelindex = fieldnames.index ("Level")
        except:
            print (f"'Level' nicht in {filename}")


    for count in range (len (pagelist)):
        newcl = Cuelist (globs.patch)
        # globs.fadertable.append (newcl) # Konstruktor
        new_cltable.append (newcl)
        fadernum = fadernum + 1 
        filename = pagelist[count]["Filename"]
        if filename == "":
            filename = "_neu"
        newcl.open (filename)
        newcl.id = newcl.location + str (count)
        newcl.text = pagelist[count]["Text"]
        newcl.text = pagelist[count]["Text"]

        # nun Midi-Requests einlesen:
        if globs.PYTHONANYWHERE == "false":
            num_controllers = len (globs.midiin)
            try:
                cnr = pagelist[count]["Midiinput"] # cnr:str ab 1 =ControllerNr
                fnr = pagelist[count]["Midifader"] # fnr:str ab 1 =FaderNr
                # print (f"Midi-Controller:{cnr}, Fader:{fnr}")
            except:
                print ("Midi-Info nicht in cuefaders")
                cnr = -1
                fnr = -1
            # cnr und fnr können '' sein:
            if cnr and fnr:
                cnr = int(cnr)-1
                fnr = int(fnr)-1
                if cnr in range(num_controllers):
                    controller = globs.midifaderlist[cnr]
                    controller[fnr] = fadernum - 1    #count
    
        # nun Levels:    
        if csvlevels_requested:        
            try:
                level = float (pagelist[count]["Level"])
            except: # Default 0.0
                level = 0.0
            newcl.level = level

    if with_savedlevels == False: # aktuelle Levels wiederherstellen
        restore_currentlevels (new_cltable, currentlevels)
        
    Cuelist.instances = new_cltable
    globs.cltable = new_cltable

