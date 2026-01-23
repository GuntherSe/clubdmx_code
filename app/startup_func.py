#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
  Startup-Funktionen
"""
import globs

import os
import os.path
import logging

from cue import Cue
from cuebutton import Cuebutton
from cuelist import Cuelist
from csvfileclass import Csvfile
from midiutils import check_midicontroller
from cuelist_utils import cuedata_view
from startup_levels import backup_currentlevels, restore_currentlevels
from startup_levels import button_locations, fader_locations

logger = logging.getLogger ("clubdmx")

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


def csvlevel_requested () -> bool:
    if globs.cfg.get("savecuelevels") == '1':
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
            item["Level"] = int (inst.level * 255)
            ret.append (item)
    return ret


# --- Fader-info ------------------------------------------------------

def make_fadertable (currentlevels:dict={}, with_currentlevels:bool=True) :
    """ Liste mit Fader-Cues erzeugen

    location: entweder 'cuefaders' oder 'exefaders'
    fadertable:  globale Liste der Cue-Fader (aus exefader und cuefader)
    Levels: 
      with_currentlevels -> currentlevels beibehalten 
      cfg ('savecuelevels') == '1' -> aus CSV-Datei einlesen 
    """
    if with_currentlevels and not len (currentlevels):
        currentlevels = backup_currentlevels ("fader") # aktuelle Level

    locations = fader_locations
    new_fadertable = []
    # aud Midi-Fadertabellen cuefader entfernen:
    if globs.PYTHONANYWHERE == "false":
        globs.midi.clear_lists ("fader", hi=globs.SHIFT)

    # sollen csv-gespeicherte Levels geladen werden?
    with_csvlevels = csvlevel_requested ()
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
            logger.error (f"'Filename' nicht in {filename}")
            continue
        
        if with_csvlevels: 
            try: # nur zur Fehler-Ausgabe
                levelindex = fieldnames.index ("Level")
            except:
                logger.error (f"'Level' nicht in {filename}")

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
                incnr = content[count]["Midiinput"]
                outcnr = content[count]["Midioutput"]
                fnr = content[count]["Midifader"]
                incnr, outcnr, fnr = check_midicontroller (incnr,outcnr,fnr)
                # Eintrag in Cue:
                newcue.midioutput = outcnr -1 
                newcue.midicontroller = fnr -1
                # Midi-Input:
                if incnr and fnr:
                    globs.midi.in_faders[incnr-1][fnr-1] = fadernum-1                    
                # Midi-Output:
                if outcnr and fnr:
                    globs.midi.out_faders[outcnr-1][fnr-1] = fadernum-1   
                    # globs.midi.out_faders[outcnr-1].append (fnr-1)
        
            # nun Levels:    
            if with_csvlevels:        
                try:
                    level = float (content[count]["Level"])
                except: # Default 0.0
                    level = 0.0
                newcue.level = level

    if with_currentlevels: # aktuelle Levels wiederherstellen
        restore_currentlevels (new_fadertable, currentlevels)
    globs.fadertable = new_fadertable


# --- Cue-Buttons -------------------------------------------------------------
def make_cuebuttons (currentlevels:dict={}, with_currentlevels:bool=True):
    """ Button-Liste erzeugen
    
    Die Liste ist  Cuebutton:instances
    Buttons finden sich in cuebutton.html, executer.html
    location: cuebuttons, exebuttons1, exebuttons2
    Levels: 
      with_currentlevels -> currentlevels beibehalten 
      cfg ('savecuelevels') == '1' -> aus CSV-Datei einlesen 
    """
    if with_currentlevels and not len (currentlevels):
        currentlevels = backup_currentlevels ("button") # aktuelle Level

    locations = button_locations
    new_buttontable = []
    # Midi-Buttontabellen löschen:
    if globs.PYTHONANYWHERE == "false":
        globs.midi.clear_lists ("button", hi=globs.SHIFT)

    # sollen csv-gespeicherte Levels geladen werden?
    with_csvlevels = csvlevel_requested ()
    butnum = 0    # zählt Buttons in allen locations

    for loc in locations:
        filename = globs.cfg.get (loc)
        csvfile = Csvfile (os.path.join (globs.room.cuebuttonpath(), filename))
        content = csvfile.to_dictlist ()
        fieldnames = csvfile.fieldnames()
        try: # nur zur Fehler-Ausgabe
            fileindex = fieldnames.index ("Filename") 
        except:
            logger.error (f"Feld 'Filename' nicht in {filename}")
            continue
        
        if with_csvlevels: 
            try: # nur zur Fehler-Ausgabe
                levelindex = fieldnames.index ("Level")
            except:
                logger.error (f"Feld 'Level' nicht in {filename}")

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
                incnr = content[count]["Midiinput"]
                outcnr = content[count]["Midioutput"]
                butnr = content[count]["Midibutton"]
                incnr, outcnr, butnr = check_midicontroller (incnr,outcnr,butnr)
                # Eintrag in Cue:
                newbut.midioutput = outcnr - 1
                newbut.midicontroller = butnr - 1
                # Midi-Input:
                if incnr and butnr:
                    globs.midi.in_buttons[incnr-1][butnr-1] = butnum-1
                # Midi-Output:
                if outcnr and butnr:
                    globs.midi.out_buttons[outcnr-1][butnr-1] = butnum-1   
                    # globs.midi.out_buttons[outcnr-1].append (butnr-1)

            # nun Levels:     
            if with_csvlevels:
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
               
    if with_currentlevels: # aktuelle Levels wiederherstellen
        restore_currentlevels (new_buttontable, currentlevels, type="button")

    Cuebutton.instances = new_buttontable
    globs.buttontable = new_buttontable

# --- Cuelist-Tabelle erzeugen ------------------------------------------------

def make_cuelistpages (currentlevels:dict={}, with_currentlevels:bool=True) :
    """ Liste mit Pages an Cuelisten erzeugen

    Levels: 
      with_currentlevels -> currentlevels beibehalten 
      cfg ('savecuelevels') == '1' -> aus CSV-Datei einlesen 
    """
    new_cltable = []
    # aus Midi-Fadertabellen cuefader entfernen:
    if globs.PYTHONANYWHERE == "false":
        globs.midi.clear_lists ("fader", lo=globs.SHIFT, hi=2*globs.SHIFT)

    # sollen csv-gespeicherte Levels geladen werden?
    if with_currentlevels and not len (currentlevels):
        currentlevels = backup_currentlevels ("cuelist") # aktuelle Level

    with_csvlevels = csvlevel_requested ()

    fadernum = globs.SHIFT # unterscheidet cuefader von cuelistfader
    filename = globs.cfg.get("pages")
    fullname = os.path.join (globs.room.pagespath() , filename)
    csvfile = Csvfile (fullname)
    pagelist = csvfile.to_dictlist ()
    fieldnames = csvfile.fieldnames()
    try: # Filename muss vorhanden sein
        fileindex = fieldnames.index ("Filename") 
    except:
        logger.error (f"'Filename' nicht in {filename}")
        return
    
    if with_csvlevels: 
        try: # nur zur Fehler-Ausgabe
            levelindex = fieldnames.index ("Level")
        except:
            logger.error (f"'Level' nicht in {filename}")


    for count in range (len (pagelist)):
        newcl = Cuelist (globs.patch)
        # globs.fadertable.append (newcl) # Konstruktor
        new_cltable.append (newcl)
        fadernum = fadernum + 1 
        # Filename != '_neu':
        filename = pagelist[count]["Filename"]
        if filename == "" or filename == "_neu":
            filename = pagelist[count]["Text"]
            colnum = fieldnames.index ("Filename") +1
            csvfile.write_cell (count+1,colnum, filename)
        # Cueliste existiert? Evtl neu erzeugen:
        clname = os.path.join (globs.room.cuelistpath(), filename)
        clfile = Csvfile (clname)
        if not clfile.exists ():
            newclname = os.path.join (globs.room.cuelistpath(), "_neu")
            newclfile = Csvfile (newclname)
            newclfile.backup (clname)

        newcl.open (filename)
        newcl.id = newcl.location + str (count)
        newcl.text = pagelist[count]["Text"]

        # nun Midi-Requests einlesen:
        if globs.PYTHONANYWHERE == "false":
            incnr =  pagelist[count]["Midiinput"]
            outcnr = pagelist[count]["Midioutput"]
            fnr =    pagelist[count]["Midifader"]
            incnr, outcnr, fnr = check_midicontroller (incnr,outcnr,fnr)
            # Eintrag in Cue:
            newcl.midioutput = outcnr -1
            newcl.midicontroller = fnr -1
            # Midi-Input:
            if incnr and fnr:
                globs.midi.in_faders[incnr-1][fnr-1] = fadernum-1
            # Midi-Output:
            if outcnr and fnr:
                globs.midi.out_faders[outcnr-1][fnr-1] = fadernum-1   
                # globs.midi.out_faders[outcnr-1].append (fnr-1) 

        # nun Levels:    
        if with_csvlevels:        
            try:
                level = float (pagelist[count]["Level"])
            except: # Default 0.0
                level = 0.0
            newcl.level = level

    if with_currentlevels: # aktuelle Levels wiederherstellen
        restore_currentlevels (new_cltable, currentlevels)
        
    Cuelist.instances = new_cltable
    globs.cltable = new_cltable
    # Cuelist View-Funktion neu zuweisen:
    Cuelist.set_vievfunction (cuedata_view)

