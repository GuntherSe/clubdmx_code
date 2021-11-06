#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
  Startup: Level Funktionen
"""
import globs

import os
import os.path
import time

from csvfileclass import Csvfile

# locations: wo kommen diese Elemente vor?
button_locations = ["cuebuttons", "exebuttons1", "exebuttons2"]
fader_locations  = ["cuefaders", "exefaders"]
cuelist_locations = ["pages"]


def activate_startcue ():
    """ Wenn in Config aktiviert, dann finde startcue in fadertable
    und setze Level auf 1
    """
    startcue = globs.cfg.get ("startcue")
    fullname = os.path.join (globs.room.cuepath (), startcue)
    csvfile = Csvfile (fullname)
    if not csvfile.exists ():
        print ("Startcue nicht gefunden.")
        return

    # in Fadertabelle Zeile mit Filename 'startcue' suchen
    found = False
    for item in globs.fadertable:
        if item.file.shortname () == startcue:
            found = True
            item.level = 1
    # in Buttontable nach 'startcue' suchen:
    if not found:
        for item in globs.buttontable:
            if item.file.shortname () == startcue:
                found = True
                item.go ()
    if not found:
        print ("Startcue weder in Fadertabelle noch in Buttontabelle.")
    # optional:             
    #     # startcue nicht gefunden, neuer Eintrag in Fadertabelle:
    #     globs.fadertable.append ( Cue(globs.patch)) # Konstruktor
    #     idx = len (globs.fadertable) - 1
    #     stcue = globs.fadertable[idx]
    #     stcue.open (startcue)
    #     stcue.level = 1
    #     # und Eintrag in Csvfile:
    #     newdata = [{"Text":"Startcue","Filename":startcue,"Level":"1"}]
    #     filename = globs.cfg.get("cuefaders")
    #     fullname = os.path.join (globs.room.cuefaderpath() , filename)
    #     c = Csvfile (fullname)
    #     c.add_lines (newdata)


# --- Backup & Restore Current Levels ---------------------------------------

def backup_currentlevels (table:str) ->dict:
    """ aktuelle cuelevels sichern 
    für jeden Cue einen eintrag in levels: Cue.count:Cue.level
    """
    levels = {}
    if table == "fader":
        cuetable = globs.fadertable
    elif table == "button":
        cuetable = globs.buttontable
    elif table == "cuelist":
        cuetable = globs.cltable

    # for i in range (len (cuetable)):
    #     key = cuetable[i].text
    #     levels[key] = cuetable[i].level

    for i, line in enumerate (cuetable):
        key = line.text
        levels[key] = line.level

    return levels


def restore_currentlevels (cuetable:str, leveldict:dict, type:str=""):
    """ die gespeicherten Levels wiederherstellen
    """
    for i, line in enumerate (cuetable):
        key = line.text
        if key in leveldict.keys ():
            line.level = leveldict[key]
            if type == "button" and leveldict[key]:  # level > 0 -> status = 1
                line.status = 1

# --------------------------------------------------------------------------
def level_to_csv (table:str):
    """ aktuelle cuelevels sichern

    levels werden beim Programmstart geladen, wenn Config "savecuelevels" == 1
    table: 'button', 'fader' oder 'cuelist'
    """
    cfgdata = globs.cfg.get("savecuelevels") # Sliderwerte intitialisieren?
    if not cfgdata or cfgdata == '0':
        return

    # savelist:  gespeicherte Daten
    # cuetable: aktuelle Daten
    
    # file öffnen, Daten einlesen,  fadertable initialisieren
    if table == "fader":
        # return
        locations = fader_locations
        loc_root = globs.room.cuefaderpath()
        cuetable = globs.fadertable
    elif table == "button":
        locations = button_locations
        loc_root = globs.room.cuebuttonpath()
        cuetable = globs.buttontable
    elif table == "cuelist":
        locations = cuelist_locations
        loc_root = globs.room.pagespath()
        cuetable = globs.cltable
    else:
        return

    for loc in locations:
        filename = globs.cfg.get (loc)
        fullname = os.path.join (loc_root, filename)
        csvfile = Csvfile (fullname)
        savelist = csvfile.to_dictlist ()
    
        try: 
            levelindex = csvfile.fieldnames().index ("Level")
        except:
            continue

        for i in range (len (savelist)):
            try:
                savedlevel = round (float (savelist[i]["Level"]), 6)
            except:
                savedlevel = 0.0
                
            # curlevel = round (cuetable[i].level, 6)
            searchid = loc + str(i)
            # in cuetable nach searchid suchen:
            found = list (filter (lambda but: but.id == searchid, cuetable))
            if found:
                curlevel = round (found[0].level, 6)
                if savedlevel != curlevel:
                    csvfile.write_cell (1+i, 1+levelindex, str(curlevel))


def autosave_cuelevels ():
    """ cuelevels sichern, Zeit warten
    """
    while True :
        level_to_csv ("fader")
        level_to_csv ("button")
        level_to_csv ("cuelist")
        time.sleep (30)


