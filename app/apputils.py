#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
Utilities:
- Datenbank Backup/Restore
- Midi Input auswerten
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
from flask import flash, redirect, url_for, request
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


def press_cuebutton (index:int, direction:int) -> int:
    """ cuebutton auf website oder midi drücken
    index: button-Nummer ab 0
    direction: 1 = press, 0 = release
    return: 1 = on, 0 = off
    """
    ret = 0
    buttons = len (globs.buttontable)
    if index in range (buttons):
        ret = globs.buttontable[index].go()
        if globs.PYTHONANYWHERE == "false" and globs.midiactive:
            buttontype = globs.buttontable[index].type
            buttongroup = globs.buttontable[index].group
            if buttontype == "Auswahl":
                for count in range (buttons):
                    item = globs.buttontable[count]
                    if item.type == "Auswahl" and item.group == buttongroup:
                        midi_monitor (count, 0)
            midi_monitor (index, ret)
    return ret


# --- MIDI Funktionen ---
# nur importieren, wenn PYTHONANYWHERE == "false"
def evaluate_midi (*data):
    """ midicontroller an requests schicken
    wird als output-Funktion für Midicontroller verwendet
    in Midicontroller.poll: self.output (index, type, cnt, self.fader_buffer[cnt
    data[0]: controller-Nummer
    data[1]: "fader" oder "button"
    data[2]: index in fadertable oder buttontable ab 0
    data[3]: Wert in 0 .. 127
    """
    if not len (globs.fadertable): # beim Neu-Laden von config möglich
        return
    # index:int=data[0], type:str=data[1], fader:int=data[2], level:int=data[3]
    if data[1]=="fader" and data[2] in globs.midifaderlist[data[0]]:
        fader =  globs.midifaderlist[data[0]][data[2]]
        if fader < 1000:
            globs.fadertable[fader].level = data[3] / 127
        else:
            globs.cltable[fader-1000].level = data[3] / 127
    elif data[1]=="button":
        try:
            index = globs.midibuttonlist[data[0]][data[2]]
            if data[3]: # nur 'drücken' auswerten, nicht 'loslassen'
                press_cuebutton (index, 1)
                # ret = globs.buttontable[index].go ()
                # midi_monitor (index, ret)
            else: # nur relevant, wenn Buttontype = Taster
                if index in range (len (globs.buttontable)):
                    buttontype = globs.buttontable[index].type
                    if buttontype == "Taster":
                        press_cuebutton (index, 0)
        except: # button nicht in requests
            pass


def midi_monitor (button:int, status:int):
    """ Button-Status per LED am midioutput anzeigen """
    if button in globs.midiout_table:
        led = int (globs.midiout_table[button]) 
        if status: # status == 1
            globs.midiout.led_on (led)
        else:
            globs.midiout.led_off (led)


def calc_mixoutput ():
    """ global mix berechnen

    da in pythonanywhere keine threads verwendet werden können,
    den mix ausrechnen bei Anzeige von /output und /stage/single
    """
    if len (globs.buttontable):
        globs.buttontable[0].calc_all_faders ()
    globs.topcue.contrib.mix_function ()


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
    if isinstance (arg[0], list):
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
            if 0.0 <= val <= 1.0:
                globs.topcue.add_item (head, args[0], int(val * 255))
        elif address == "/clear":
            # topcue clear
            globs.topcue.clear()
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
                    print (f"go: {num}")
                    cl.go ()
                elif len (args) >= 2: # args > 2 ignorieren
                    print (f"go: {num}, next = {args[1]}")
                    cl.go (args[1])

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

        # else:
            # # Button, Fader
            # adr = address.split (sep='/')
            # try:
            #     num = int (adr[2])
            # except:
            #     return

            # if adr[1] == "button":
            #     id = "cuebuttons" + str (num-1)
            #     but = search_for (id, globs.buttontable)
            #     if but:
            #         but.go ()
            #     # if 0 <= num-1 < len (globs.buttontable):
            #     #     globs.buttontable[num-1].go()
            # elif adr[1] == "exebutton1":
            #     id = "exebuttons1" + str (num-1)
            #     but = search_for (id, globs.buttontable)
            #     if but:
            #         but.go ()
            # elif adr[1] == "exebutton2":
            #     id = "exebuttons2" + str (num-1)
            #     but = search_for (id, globs.buttontable)
            #     if but:
            #         but.go ()
            
            # elif adr[1] == "fader":
            #     try:
            #         faderval = float (args[0])
            #     except:
            #         return
            #     id = "cuefaders" + str (num-1)
            #     fader = search_for (id, globs.fadertable)
            #     if fader and 0.0 <= faderval <= 1.0:
            #         fader.level = faderval
            #     # if 0 <= num-1 < len (globs.fadertable) and 0.0 <= faderval <= 1.0:
            #     #     globs.fadertable[num-1].level = faderval
            # elif adr[1] == "exefader":
            #     try:
            #         faderval = float (args[0])
            #     except:
            #         return
            #     id = "exefaders" + str (num-1)
            #     fader = search_for (id, globs.fadertable)
            #     if fader and 0.0 <= faderval <= 1.0:
            #         fader.level = faderval
            
            