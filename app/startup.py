#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
Startup:
  Config laden, Daten in globale Objekte laden.
  In app.csv finden sich die Infos, um die zuletzt geladene Config und Raum
  wiederherzustellen.
"""
import globs

import os
import os.path

# from flask import current_app as app

from configclass  import Config
from roomclass import Room
#from csvnameclass import Csvname
from csvfileclass import Csvfile
from cue import Cue
from cuelist import Cuelist
from startup_func import del_cuetables, del_midilists
from startup_func import make_cuebuttons, make_fadertable, make_cuelistpages
from startup_levels import activate_startcue

if os.environ.get ("PYTHONANYWHERE")  != "true":
    from midiinput import MidiInput

current_room = ""

def get_roompath ():
    """ Basis Raumpfad ermitteln:

    - aus globs.cfgbase (= '.app.csv')
    - wenn da nicht vorhanden oder kein Verzeichnis: neues Verzeichnis
      'clubdmx_rooms' anlegen
    roombase: Ordner, der alle Räume (=subdirs) enthält
    roompath: Pfad zu dem zuletzt verwendeten Raum = roombase + subdir
    roompath ist in current_room gespeichert
    """
    global current_room
    roombase = os.environ.get ("CLUBDMX_ROOMPATH")
    roompath = globs.cfgbase.get ("room")
    # Roombase kann mit Environment-Variablen verändert werden, daher:
    # roompath aus roombase und zuletzt verwendeten Raum erzeugen
    if roombase:
        # print (f"Roombase: {roombase}")
        if roompath:
            # print (f"Roompath: {roompath}")
            root, subdir = os.path.split (roompath)
            roompath = os.path.join (roombase, subdir)
        else:
            roompath = os.path.join (roombase, "_neu")
    else:
        # if roompath: nichts zu tun
        if not roompath:
            print ("Raumverzeichnis nicht definiert. clubdmx_rooms wird verwendet.")
            root, codedir = os.path.split (globs.basedir)
            # root: eine Ebene über codepath
            # clubdmx_rooms liegt im selben Ordner wie clubdmx_code
            roompath = os.path.join (root, "clubdmx_rooms", "_neu")
    # nun ist der String 'roompath' erzeugt.
    
    if not os.path.isdir (roompath):
        print (f"Roompath nicht vorhanden, erzeuge {roompath} ")
        os.makedirs (roompath)
    globs.cfgbase.set ("room", roompath)
    globs.cfgbase.save_data ()
    current_room = roompath
   

def check_csvfile (name:str, subdir:str) -> bool:
    """ File auf Existenz prüfen """
    global current_room    
    fullname = os.path.join (current_room, subdir, name)
    csvfile = Csvfile (fullname)
    return csvfile.exists ()


def check_config (fullname:str) -> dict:
    """ Config prüfen

    - Default Config laden. Damit sind alle Keys definiert. 
    - fullname in tempcheck kopieren
    - default config speichern als fullname
    - für alle Werte von checkconf prüfen ob in tempconfig existiert, 
      dann tempconfig Wert übernehmen
    - Existenz von Files prüfen
    return: Message
    """

    ret = {}
    defaultroom = Room ()

    checkcsv = Csvfile (fullname)
    # fullname Existenz:
    if os.path.isfile (checkcsv.name()):
        config_exist = True
        head, tail = os.path.split (fullname)
        tmpname = os.path.join (head, "tempcheck" )
        checkcsv.backup (tmpname)
        tmpconfig = Config (tmpname)
    else:
        config_exist = False

    # default Config sichern als checkconf
    defaultname = os.path.join (defaultroom.configpath(), "_neu")
    defaultcsv = Csvfile (defaultname)
    defaultcsv.backup (fullname) # default nach fullname kopieren
    checkconf = Config (fullname)

    if config_exist:
        # Daten aus tmpconfig übernehmen:
        chkdata = checkconf.data ()
        for key in chkdata.keys ():
            val = tmpconfig.get (key)
            if val: #key vorhanden und hat Wert != ''
                checkconf.set (key, val)
        # nun sollten in chkconf nur mehr zulässige keys mit Werten 
        # vorhanden sein
        # tmpname löschen:
        tmpcsv = Csvfile (tmpname)
        tmpcsv.remove ()

    # Files prüfen:
    if not check_csvfile (checkconf.get ("patch"), "patch"):
        checkconf.set ("patch", "_neu")
    if not check_csvfile (checkconf.get ("cuefaders"), "cuefader"):
        checkconf.set ("cuefaders", "_neu")
    if not check_csvfile (checkconf.get ("cuebuttons"), "cuebutton"):
        checkconf.set ("cuebuttons", "_neu")
    if not check_csvfile (checkconf.get ("pages"), "pages"):
        checkconf.set ("pages", "_neu")
    if not check_csvfile (checkconf.get ("stage"), "stage"):
        checkconf.set ("stage", "_neu")
    if not check_csvfile (checkconf.get ("startcue"), "cue"):
        checkconf.set ("startcue", "_neu")
    
    # sichern
    checkconf.save_data ()
    ret["message"] = "Config ok."
    ret["category"] = "info"
    return ret


def load_config (with_savedlevels=False):
    """ cfg initialisieren bzw. neu laden
    
    cfgbase: hier sind der Name der Config-Datei und der Raum-Pfad gespeichert
    with_savedlevels==True:  levels von CSV-File 
    with_savedlevels==False: levels sind 0
    """
    global current_room
    # config-Name:
    cfgname = globs.cfgbase.get ("config")
    if not cfgname:
        cfgname = "_neu"
        globs.cfgbase.set ("config", cfgname)
        globs.cfgbase.save_data ()

    # Raum-Pfad und davon abhängige Dirs:
    get_roompath () # in global current_room gespeichert
    globs.room.set_path (current_room)
    globs.patch.set_path   (current_room)
    Cue.set_path  (current_room)
    Cuelist.set_path (current_room)

    # zur Absturzvermeidung: fadertable und buttontable löschen:
    # damit gibt es auch keine aktuellen Levels
    del_cuetables ()

    # jetzt config laden:
    fullname = os.path.join (globs.room.configpath(), cfgname)
    
    ret = check_config (fullname)
    # nun sind alle keys vorhanden und alle Files existieren
    print (ret["message"])
    globs.cfg.open (fullname)

    cfgdata = globs.cfg.get("patch")
    ret = globs.patch.open (cfgdata)

    cfgdata = globs.cfg.get("universes")
    globs.patch.set_universes (int(cfgdata))

    cfgdata = globs.cfg.get("ola_ip")
    globs.ola.set_ola_ip (cfgdata)

    if globs.PYTHONANYWHERE == "false":
    # MIDI auswerten
        cfgdata = globs.cfg.get ("midi_on") 
        if cfgdata == "1": 
            globs.midiactive = True
            if MidiInput.paused:
                MidiInput.resume ()
            # MIDI-Input:
            for i in range (4): # max 4 Midi-Controller
                num = str (1+i)
                device = globs.cfg.get("midi_input_"+num)
                # if device:
                try:
                    devnum = int(device)
                except:
                    devnum = -1 # kein Midi
                globs.midiin[i].set_device (devnum)
            # MIDI-Output:
            device = globs.cfg.get ("midi_output")
            globs.midiout.set_device (int(device))
        else:
            globs.midiactive = False
            if MidiInput.paused == False:
                MidiInput.pause ()
    # OSC Input:
        cfgdata = globs.cfg.get ("osc_input")
        if cfgdata == "1":
            cfgdata = globs.cfg.get ("osc_inputport")
            try:
                port = int (cfgdata)
            except:
                port = 8800
            ret = globs.oscinput.set_port (port)
            print (ret["message"])
            globs.oscinput.resume ()
        else:
            globs.oscinput.pause ()

    # start mit startcue?
    start_with_cue = globs.cfg.get ("start_with_cue")
    if start_with_cue == "1":
        # savecuelevels auf 0 setzen, nur eine der beiden Optionen sinnvoll:
        globs.cfg.set ("savecuelevels", "0")
        # suchen und Auswerten des Startcues erst nachdem
        # die Fadertabelle erzeugt ist.

    del_midilists ()
    make_fadertable (with_savedlevels=with_savedlevels)
    make_cuebuttons (with_savedlevels=with_savedlevels)
    make_cuelistpages (with_savedlevels=with_savedlevels)

    if start_with_cue == "1":
        activate_startcue ()

