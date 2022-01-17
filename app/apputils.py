#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
Utilities:
- Datenbank Backup/Restore
- Buttonstatus an Midioutput schicken
- mix für pythonanywhere ausrechnen
- OSC Input auswerten
"""

import globs

import os
import os.path
import shutil
from socket import gethostname

import mount as mount

# if os.environ.get ("PYTHONANYWHERE")  != "true":
#     from midioutput import MidiOutput

from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for, request, session
from startup_levels import button_locations, fader_locations

# --- Redirect back Funktion -------------------------------------
# siehe: https://stackoverflow.com/questions/14277067/redirect-back-in-flask

def redirect_url (default='basic.index'):
    return  request.args.get('next') or \
            request.referrer or \
            url_for(default)

# --- Dekoratoren ----------------------------------------------------

def admin_required (func):
    """ Decorator zur Verifizierung des Admin-Status
    """
    @wraps (func)
    def wrapper (*args, **kwargs):
        if current_user.role == "admin":
            return func (*args, **kwargs)

        flash("Nur Benutzer mit Admin-Rechten können diese Funktion nutzen.")
        return redirect (redirect_url())
        # return redirect (url_for('auth.login'))       
    return wrapper
            

def standarduser_required (func):
    """ Decorator zur Verifizierung des Standard-User-Status
    """
    @wraps (func)
    def wrapper (*args, **kwargs):
        if current_user.role == "admin" or current_user.role == "standard":
            return func (*args, **kwargs)

        flash("Nur Benutzer mit Standard- oder Admin-Rechten können diese Funktion nutzen.")
        return redirect (redirect_url())
        # return redirect (url_for('auth.login'))       
    return wrapper


# --- Datenbank Backup/Restore ---------------------------------------------

def dbbackup (dest:str) -> dict:
    """ app.db  nach dest sichern
    dest: "USB-Pfad"
    Backup-Ziel ist identifiziert durch hostname
    return: Message
    """
    ret = {}
    apppath = globs.basedir
    appdb = os.path.join (apppath, ".app.db")
    hostname = gethostname ()
    # print ("Hostname: ", hostname)
    destdbname = hostname + os.extsep + "db"

    mount.mnt.mount (dest)
    mediapath = mount.mnt.get_media_path (dest)
    destpath = os.path.join (mediapath, "clubdmx_backup")
    if not os.path.isdir (destpath):  # existiert noch nicht
        os.makedirs (destpath)
    destdb = os.path.join (destpath, destdbname)
    try:
        shutil.copyfile (appdb, destdb)
        ret["category"]="success"
        ret["message"] = f"Backup der User-Datenbank: {destdb} "
    except OSError as why:
        ret["category"]="danger"
        msg = "Backup-Fehler: " + str (why)
        ret["message"] = msg

    mount.mnt.unmount (dest)
    return ret


def dbrestore (src:str) -> dict:
    """ User-DB vom USB-Stick nach app.db kopieren 
    src: USB_pfad
    return: Message
    """
    ret = {}
    apppath = globs.basedir
    appdb = os.path.join (apppath, ".app.db")
    hostname = gethostname ()
    # print ("Hostname: ", hostname)
    srcdbname = hostname + os.extsep + "db"

    mount.mnt.mount (src)
    mediapath = mount.mnt.get_media_path (src)
    srcpath = os.path.join (mediapath, "clubdmx_backup")
    srcdb = os.path.join (srcpath, srcdbname)
    if not os.path.isfile (srcdb):  # existiert nicht
        ret["category"]="danger"
        msg = f"Restore-Fehler: {srcdb} nicht gefunden" 
        ret["message"] = msg
        mount.mnt.unmount (src)
        return ret

    try:
        shutil.copyfile (srcdb, appdb)
        ret["category"]="success"
        ret["message"] = f"Restore der User-Datenbank: {srcdb} "
    except OSError as why:
        ret["category"]="danger"
        msg = "Restore-Fehler: " + str (why)
        ret["message"] = msg

    mount.mnt.unmount (src)
    return ret


def calc_mixoutput ():
    """ global mix berechnen

    da in pythonanywhere keine threads verwendet werden können,
    den mix ausrechnen bei Anzeige von /output und /stage/single
    """
    if len (globs.buttontable):
        globs.buttontable[0].calc_all_faders ()
    globs.topcue.contrib.mix_function ()
    if len (globs.cltable):
        globs.cltable[0].calc_all_cuelists ()


def evaluate_osc (address, *arg):
    """ OSC Input je nach Adresse auswerten
    
    adress: OSC String 
    *args: restliche Parameter
    /head <Attribut> <Headnr> <Level> -> topcue.add_item
    /clear -> topcue.clear
    /fader/<nummer> <Level> -> Fader Level
    /button/<nummer> -> Button Go
    """
    def search_for (id:str, srchlist:list):
        # suche elem in srchlist mit elem[id] == id
        for elem in srchlist:
            if elem.id == id:
                return elem
        return False

    buttonaddr = ["/button", "/exebutton1", "/exebutton2"]
    faderaddr  = ["/fader", "/exefader"]
    if len(arg) and isinstance (arg[0], list):
        args = arg[0]
    else:
        args = arg

    if not globs.oscinput.paused:
        if address == "/head":
            # args: Attribut, Head-Nr, Level
            try:
                head = str (int (args[1])) # Test, ob Headnummer
                val = float (args[2])
            except:
                return
            # prüfen, ob Head und Attrib existieren:
            if head not in globs.patch.headlist ():
                return
            if args[0] not in globs.patch.attriblist(head):
                return
            if 0.0 <= val <= 1.0:
                globs.topcue.add_item (head, args[0], int(val * 255))
        elif address == "/clear":
            # topcue clear
            globs.topcue.clear()
            # session.pop ("topcuecontent", None)
        elif address == "/go":
            # args: cuelist-Nr in Pages-Seite [, next cue ]
            try:
                num = int (args[0])
            except:
                return
            id = "pages" + str (num-1)
            cl = search_for (id, globs.cltable)
            if cl:
                if len (args) == 1:
                    # print (f"go: {num}")
                    cl.go ()
                elif len (args) >= 2: # args > 2 ignorieren
                    # print (f"go: {num}, next = {args[1]}")
                    cl.go (args[1])

        elif address == "/pause":
            # args: cuelist-Nr in Pages-Seite [, next cue ]
            try:
                num = int (args[0])
            except:
                return
            id = "pages" + str (num-1)
            cl = search_for (id, globs.cltable)
            if cl:
                if len (args) == 1:
                    cl.pause ()

        elif address == "/cuelistfader":
            # args: cuelist-Nr, level
            try:
                num = int (args[0])
                val = float (args[1])
            except:
                return
            id = "pages" + str (num-1)
            cl = search_for (id, globs.cltable)
            if cl and  0.0 <= val <= 1.0:
                cl.level = val

        # cuebuttons:
        elif address in buttonaddr:
            #arg: Nr in buttontable
            try:
                num = int (args[0])
            except:
                return
            pos = buttonaddr.index (address)
            id = button_locations[pos] + str (num-1)
            but = search_for (id, globs.buttontable)
            if but:
                but.go ()

        #cuefader
        elif address in faderaddr:
            # args: Nr. in fadertable, level
            try:
                num = int (args[0])
                val = float (args[1])
            except:
                return
            pos = faderaddr.index (address)
            id = fader_locations[pos] + str (num-1)
            fader = search_for (id, globs.fadertable)
            if fader and 0.0 <= val <= 1.0:
                fader.level = val
                