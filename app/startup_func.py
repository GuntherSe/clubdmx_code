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
    """ globale midiin_faders und midiin_buttons leeren
    """
    if globs.PYTHONANYWHERE == "false":
        num_controllers = len (globs.midiin)
        globs.midiin_faders   = [{} for i in range (num_controllers)]
        globs.midiin_buttons  = [{} for i in range (num_controllers)]    
        globs.midiout_buttons = [[] for i in range (num_controllers)]
        globs.midiout_faders  = [[] for i in range (num_controllers)]


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

    locations = fader_locations
    new_fadertable = []
    if globs.PYTHONANYWHERE == "false":
        num_controllers = len (globs.midiin)

    # sollen csv-gespeicherte Levels geladen werden?
    csvlevels_requested = check_levelrequest (with_savedlevels)
    fadernum = 0
    for loc in locations:
        filename = globs.cfg.get(loc)
        fullname = os.path.join (globs.room.cuefaderpath() , filename)
        csvfile = Csvfile (fullname)
        content = csvfile.to_dictlist ()
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


        for count in range (len (content)):
            newcue = Cue (globs.patch)
            new_fadertable.append (newcue)
            fadernum = fadernum + 1 
            filename = content[count]["Filename"]
            if filename == "":
                filename = "_neu"
            newcue.open (filename)
            newcue.location = loc
            newcue.id = loc + str (count)
            newcue.text = content[count]["Text"]

            # nun Midi-Requests einlesen:
            if globs.PYTHONANYWHERE == "false":
                num_controllers = len (globs.midiin)
                # Midiinput-Nummer, Zählung ab 1:
                try: 
                    incnr = int (content[count]["Midiinput"])
                    if not (1 <= incnr <= num_controllers):
                        incnr = 0
                except:
                    incnr = 0
                # Midioutput-Nummer, Zählung ab 1:
                try: 
                    outcnr = int (content[count]["Midioutput"])
                    if not (1 <= outcnr <= num_controllers):
                        outcnr = 0
                except:
                    outcnr = 0
                newcue.midioutput = outcnr -1 
                # MidiFader-Nummer, Zählung ab 1:
                try: 
                    fnr = int (content[count]["Midifader"])
                except:
                    fnr = 0
                newcue.midicontroller = fnr -1
                # Midi-Input:
                if incnr and fnr:
                    globs.midiin_faders[incnr-1][fnr-1] = fadernum-1
                # Midi-Output:
                if outcnr and fnr:
                    # globs.midiout_faders[outcnr-1][fnr-1] = fadernum-1   
                    globs.midiout_faders[outcnr-1].append (fnr-1)
        
            # nun Levels:    
            if csvlevels_requested:        
                try:
                    level = float (content[count]["Level"])
                except: # Default 0.0
                    level = 0.0
                newcue.level = level

    if with_savedlevels == False: # aktuelle Levels wiederherstellen
        restore_currentlevels (new_fadertable, currentlevels)
    globs.fadertable = new_fadertable


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

    locations = button_locations
    new_buttontable = []

    # sollen csv-gespeicherte Levels geladen werden?
    csvlevels_requested = check_levelrequest (with_savedlevels)
    butnum = 0    # zählt Buttons in allen locations

    for loc in locations:
        filename = globs.cfg.get (loc)
        csvfile = Csvfile (os.path.join (globs.room.cuebuttonpath(), filename))
        content = csvfile.to_dictlist ()
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

        for count in range (len (content)):
            newbut = Cuebutton(globs.patch) # Konstruktor
            new_buttontable.append (newbut)
            butnum = butnum + 1
            filename = content[count]["Filename"]
            if filename == "":
                filename = "_neu"
            newbut.open (filename)
            newbut.location = loc
            newbut.id = loc + str (count)
            newbut.text = content[count]["Text"]

            # Zeiten einlesen:
            newbut.fade_in = float (content[count]["Fadein"])
            newbut.fade_out = float (content[count]["Fadeout"])
            # Type (Schalter, Taster, Auswahl) und Group einlesen:
            newbut.type = content[count]["Type"] 
            newbut.group = int (content[count]["Group"])

            # nun Midi-Requests einlesen:
            if globs.PYTHONANYWHERE == "false":
                num_controllers = len (globs.midiin)
                # Midiinput-Nummer, Zählung ab 1:
                try: 
                    incnr = int (content[count]["Midiinput"])
                    if not (1 <= incnr <= num_controllers):
                        incnr = 0
                except:
                    incnr = 0
                # Midioutput-Nummer, Zählung ab 1:
                try: 
                    outcnr = int (content[count]["Midioutput"])
                    if not (1 <= outcnr <= num_controllers):
                        outcnr = 0
                except:
                    outcnr = 0
                newbut.midioutput = outcnr - 1
                # MidiButton-Nummer, Zählung ab 1:
                try: 
                    butnr = int (content[count]["Midibutton"])
                except:
                    butnr = 0
                newbut.midicontroller = butnr - 1
                # Midi-Input:
                if incnr and butnr:
                    globs.midiin_buttons[incnr-1][butnr-1] = butnum-1
                # Midi-Output:
                if outcnr and butnr:
                    # globs.midiout_buttons[outcnr-1][butnr-1] = butnum-1   
                    globs.midiout_buttons[outcnr-1].append (butnr-1)

            # nun Levels:     
            if csvlevels_requested:
                try:
                    level = float (content[count]["Level"])
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

    Cuebutton.instances = new_buttontable
    globs.buttontable = new_buttontable

# --- Cuelist-Tabelle erzeugen ------------------------------------------------

def make_cuelistpages (with_savedlevels:bool=False) :
    """ Liste mit Pages an Cuelisten erzeugen

    falls in config angegeben, dann Levels einlesen
    """
    new_cltable = []

    # sollen csv-gespeicherte Levels geladen werden?
    currentlevels = backup_currentlevels ("cuelist") # aktuelle Level
    csvlevels_requested = check_levelrequest (with_savedlevels)

    fadernum = globs.SHIFT # unterscheidet fader von cuefader
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

        # nun Midi-Requests einlesen:
        if globs.PYTHONANYWHERE == "false":
            num_controllers = len (globs.midiin)
            # Midiinput-Nummer, Zählung ab 1:
            try: 
                incnr = int (pagelist[count]["Midiinput"])
                if not (1 <= incnr <= num_controllers):
                    incnr = 0
            except:
                incnr = 0
            # Midioutput-Nummer, Zählung ab 1:
            try: 
                outcnr = int (pagelist[count]["Midioutput"])
                if not (1 <= outcnr <= num_controllers):
                    outcnr = 0
            except:
                outcnr = 0
            newcl.midioutput = outcnr -1
            # MidiFader-Nummer, Zählung ab 1:
            try: 
                fnr = int (pagelist[count]["Midifader"])
            except:
                fnr = 0
            newcl.midicontroller = fnr -1
            # Midi-Input:
            if incnr and fnr:
                globs.midiin_faders[incnr-1][fnr-1] = fadernum-1
            # Midi-Output:
            if outcnr and fnr:
                # globs.midiout_faders[outcnr-1][fnr-1] = fadernum-1   
                globs.midiout_faders[outcnr-1].append (fnr-1) 

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

