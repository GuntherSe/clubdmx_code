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
import logging

from configclass  import Config
from roomclass import Room
#from csvnameclass import Csvname
from csvfileclass import Csvfile
from cue import Cue
from cuelist import Cuelist
from startup_func import del_cuetables
from startup_func import make_cuebuttons, make_fadertable, make_cuelistpages
from startup_levels import activate_startcue
from midiutils import eval_midiinput, get_midicommandlist

if os.environ.get ("PYTHONANYWHERE")  != "true":
    from mido_input import Midi

current_room = ""

logger = logging.getLogger ("clubdmx")

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
        logger.info (f"Roombase: {roombase}")
        if roompath:
            root, subdir = os.path.split (roompath)
            roompath = os.path.join (roombase, subdir)
        else:
            roompath = os.path.join (roombase, "_neu")
    else:
        # if roompath: nichts zu tun
        if not roompath:
            logger.info ("Raumverzeichnis nicht definiert. clubdmx_rooms wird verwendet.")
            root, codedir = os.path.split (globs.basedir)
            # root: eine Ebene über codepath
            # clubdmx_rooms liegt im selben Ordner wie clubdmx_code
            roompath = os.path.join (root, "clubdmx_rooms", "_neu")
    # nun ist der String 'roompath' erzeugt.
    logger.info (f"Roompath: {roompath}")
    
    if not os.path.isdir (roompath):
        logger.warning (f"Roompath nicht vorhanden, erzeuge {roompath} ")
        os.makedirs (roompath)
    globs.cfgbase.set ("room", roompath)
    globs.cfgbase.save_data ()
    current_room = roompath
   

def check_csvfile (name:str, subdir:str) -> bool:
    """ File auf Existenz prüfen """
    global current_room    
    fullname = os.path.join (current_room, subdir, name)
    csvfile = Csvfile (fullname)
    found = csvfile.exists ()
    if found:
        logger.info (f"{subdir}/{name} vorhanden.") 
    else:
        logger.warning (f"{subdir}/{name} nicht vorhanden.") 
    return found


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
        tmpconfig = Config (fullname)
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
    logger.info (ret["message"])
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
            # globs.midi.reset_pygame ()
            globs.midiactive = True
            if Midi.paused:
                Midi.resume ()
            # MIDI-Input:
            for i in range (4): # max 4 Midi-Controller
                num = str (1+i)
                device = globs.cfg.get("midi_input_"+num)
                # if device:
                try:
                    devnum = int(device)
                except:
                    devnum = -1 # kein Midi
                ret = globs.midi.set_indevice (i, devnum)
                if ret["category"] != "success":
                    globs.midi.set_indevice (i, -1)
                    globs.cfg.set ("midi_input_"+num, -1)
            # MIDI-Output:
                device = globs.cfg.get ("midi_output_"+num)
                try:
                    devnum = int(device)
                except:
                    devnum = -1 # kein Midi
                ret = globs.midi.set_outdevice (i, devnum)
                if ret["category"] != "success":
                    globs.midi.set_outdevice (i, -1)
                    globs.cfg.set ("midi_output_"+num, -1)
            globs.midi.set_eval_function (eval_midiinput)
        else:
            globs.midiactive = False
            if Midi.paused == False:
                Midi.pause ()
        # OSC Input:
        cfgdata = globs.cfg.get ("osc_input")
        if cfgdata == "1":
            cfgdata = globs.cfg.get ("osc_inputport")
            try:
                port = int (cfgdata)
            except:
                port = 8800
            ret = globs.oscinput.set_port (port)
            logger.info (ret["message"])
            globs.oscinput.resume ()
        else:
            globs.oscinput.pause ()

        globs.midi.clear_lists ()
        get_midicommandlist ()

    # start mit startcue?
    start_with_cue = globs.cfg.get ("start_with_cue")
    if start_with_cue == "1":
        # savecuelevels auf 0 setzen, nur eine der beiden Optionen sinnvoll:
        globs.cfg.set ("savecuelevels", "0")
        # suchen und Auswerten des Startcues erst nachdem
        # die Fadertabelle erzeugt ist.

    make_fadertable (with_savedlevels=with_savedlevels)
    make_cuebuttons (with_savedlevels=with_savedlevels)
    make_cuelistpages (with_savedlevels=with_savedlevels)

    if start_with_cue == "1":
        activate_startcue ()

