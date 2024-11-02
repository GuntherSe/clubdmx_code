#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Raum-Views """

import os
import os.path
import shutil # fürs kopieren

from flask import Blueprint, request, json, flash, current_app
from flask import redirect, url_for, render_template, session
from flask import send_from_directory #, jsonify

from csvnameclass import Csvname
from roomclass import Room
from startup import load_config
from apputils import standarduser_required, admin_required, redirect_url

import globs

room = Blueprint ("room", __name__, url_prefix="/room",
                    static_folder="static", template_folder="templates")

# beim Wechsel des Raums: Sessionvariablen löschen
def clear_session_subdirs ():
    """ Session-Variablen löschen 
    
    in csv-Views beim Anzeigen der Datenbank-Tabellen gesetzt.
    (siehe Funktion gettable)
    """
    for subdir in globs.room.subdirs:
        storename = "visible"+subdir
        if storename in session:
            session.pop (storename)



@room.route ("/change", methods = ["GET","POST"])
def change ():
    """ Raumverzeichnis wechseln """
    if request.method == 'POST':
        try:
            newpath = request.form["path"]
        except:
            flash ("Kein Pfad angegeben", category="danger")
            return "not ok"

        newpath = newpath.replace ('+', os.sep) # '+' in '/' umwandeln
        globs.room.set_path (newpath)
        flash ("in neuen Raum wechseln.", category="success")
        # Raum prüfen:
        globs.room.check_fields ()
        globs.cfgbase.set ("room", newpath)
        # hier einfügen: config Name festlegen
        head, tail = os.path.split (newpath)
        # wenn config mit Namen 'tail' existiert,
        # dann diese config laden.
        # sonst config '_neu' laden und als 'tail' sichern .
        fname = os.path.join (globs.room.configpath(), tail)
        cfgfile = Csvname (fname)
        if cfgfile.exists ():
            globs.cfgbase.set ("config", tail)
        else:
            newname = os.path.join (globs.room.configpath(), "_neu")
            cfgfile.name (newname)
            cfgfile.backup (tail)
        globs.cfgbase.set ("config", tail)
        globs.cfgbase.save_data ()
        load_config (with_savedlevels=True)
        flash (f"und nun Konfiguration {tail} öffnen!", category="info")
        clear_session_subdirs () 
        if "stagename" in session: 
            session.pop ("stagename")
        if "selected_cuelist" in session:
            session.pop ("selected_cuelist")

        return "ok"

    rootpath = globs.room.rootpath().replace (os.sep, '+')
    ret ={}
    ret["spath"] = rootpath
    ret["updir"] = "true"
    ret["dialogbox"] = render_template ("modaldialog.html", body="filedialog",
                       title = "Raum wählen")
    return json.dumps (ret)


@room.route ("/rename", methods = ["GET","POST"])
@admin_required
def rename ():
    """ Raum umbenennen 
    
    Falls config-Name == Raumverzeichnis-Name, dann config umbenennen
    """

    if request.method == 'POST':
        newroom = request.form ["name"]

        if newroom and newroom != "undefined":
            # currentconfname = globs.cfg.file.name ()
            oldroomname = globs.room.name()
            ret = globs.room.rename (newroom)
            if ret["category"] == "success":
                globs.cfgbase.set ("room", globs.room.path())
                # config umbenennen, wenn config-Name == room-Name:
                currentcfg = globs.cfg.file.shortname()
                if currentcfg == oldroomname:
                    fname = os.path.join (globs.room.configpath(), newroom)
                    cfgfile = Csvname (fname)
                    if cfgfile.exists (): # löschen und aktuelle config umbenennen
                        cfgfile.remove ()
                    globs.cfg.file.rename (newroom)
                    globs.cfgbase.set ("config", newroom)
                # else: Config bleibt gleich
                globs.cfgbase.save_data ()

                # globs.cfg.open (cfgfile.name()) # notwendig?
                load_config (with_savedlevels=True)
                flash (f"Raum umbenannt: {newroom}")
            else:
                flash ("Raum konnte nicht umbenannt werden.", category="danger")
            return "ok"
        else:
            flash ("kein Name angegeben.", category="danger")
            return "ok"
    return render_template ("modaldialog.html", title="Raum-Verwaltung",
                                                text="Den Raum umbenennen:",
                                                body="stringbody",
                                                submit_text="umbenennen")


@room.route ("/saveas", methods = ["GET","POST"])
@standarduser_required
def saveas ():
    """ Raum unter neuem Namen sichern 
    Filedialog aufrufen (damit die vorhandenen Räume sichtbar sind)
    Auswahl: Bestehenden Raum anwählen oder neuen Namen eintragen
    """
    oldname = globs.room.name ()
    if request.method == 'POST':
        newname = request.form["filename"]
        if newname != '' and newname != "undefined":
            newpath = os.path.join (globs.room.rootpath (), newname)
        else:
            newpath = request.form["path"]
            newpath = newpath.replace ('+', os.sep) # '+' in '/' umwandeln
            head,newname = os.path.split (newpath)

        globs.room.backup (newpath)
        # in newpath wechseln:
        globs.room.set_path (newpath)
        # da gleiche config, kann load_config entfallen
        globs.cfgbase.set ("room", globs.room.path())
        # config umbenennen:
        currentcfg = globs.cfg.file.shortname()
        if currentcfg == oldname:
            fname = os.path.join (globs.room.configpath(), newpath)
            cfgfile = Csvname (fname)
            if cfgfile.exists (): # löschen und aktuelle config umbenennen
                cfgfile.remove ()
            globs.cfg.file.rename (newpath)
            globs.cfgbase.set ("config", newpath)
        # else: Config bleibt gleich

        globs.cfgbase.save_data ()
        flash (f"Raum {oldname} gesichert unter {newname}.")
        return "ok"

    rootpath = globs.room.rootpath().replace (os.sep, '+')
    ret ={}
    ret["spath"] = rootpath
    # ret["updir"] = "true"
    ret["dialogbox"] = render_template ("modaldialog.html", body="filedialog",
                       title = f"Raum {oldname} sichern als ...")
    return json.dumps (ret)


@room.route ("/remove", methods = ["GET","POST"])
@admin_required
def remove ():
    """ Raum löschen
    Filedialog aufrufen (damit die vorhandenen Räume sichtbar sind)
    Auswahl: Bestehenden Raum anwählen oder Namen eintragen
    """
    if request.method == 'POST':
        delname = request.form["filename"]
        if delname != '' and delname != "undefined":
            delpath =  os.path.join (globs.room.rootpath (), delname)
        else:
            delpath = request.form["path"]
            delpath = delpath.replace ('+', os.sep) # '+' in '/' umwandeln

        if delpath == globs.room.rootpath ():
            flash ("Kein Raum angegeben.")
            return "ok"

        ret = globs.room.remove (delpath)
        flash (ret["message"], category=ret["category"])
        return "ok"

    rootpath = globs.room.rootpath().replace (os.sep, '+')
    ret ={}
    ret["spath"] = rootpath
    ret["dialogbox"] = render_template ("modaldialog.html", body="filedialog",
                       title = "Raum löschen")
    return json.dumps (ret)


@room.route ("/new", methods = ["GET","POST"])
def new ():
    """ neuen Raum erstellen """

    if request.method == 'POST':
        newroom = request.form ["name"]

        if newroom and newroom != "undefined":
            fullpath = os.path.join (globs.room.rootpath(), newroom)
            if os.path.isdir (fullpath): # bereits vorhanden -> leeren
                globs.room.set_path (fullpath)
                globs.room.empty ()
            else:
                newproj = Room (fullpath)

            globs.cfgbase.set ("room", fullpath)
            # config Name = room Name:
            newname = os.path.join (globs.room.configpath(), "_neu")
            cfgfile = Csvname (newname)
            cfgfile.backup (os.path.join (fullpath, newroom))
            globs.cfgbase.set ("config", newroom)
            globs.cfgbase.save_data ()

            load_config ()
            flash (f"in neuen Raum wechseln: {newroom}", category="success")
            clear_session_subdirs ()
            return "ok"
        else:
            flash ("kein Name angegeben.", category="danger")
            return "not ok"
    return render_template ("modaldialog.html", title="Raum-Verwaltung",
                                                text="Einen neuen Raum erstellen:",
                                                body="stringbody",
                                                submit_text="erstellen")


@room.route ("/restoresource", methods = ["GET","POST"])
def restoresource ():
    """ Raumverzeichnis vom USB Backup auswählen 

    Das Verzeichnis wird nicht direkt ausgewählt, sondern ein
    Alias, der durch room.usbmapping() erzeugt wurde
    """

    if request.method == 'POST':
        try:
            newpath = request.form["shortname"]
        except:
            flash ("Kein Backup angegeben", category="danger")
            return "not ok"

        if "usbdrive" in session:
            usbdrv = session["usbdrive"]
            session.pop ("usbdrive", None)
            ret = globs.room.usbrestore (usbdrv, newpath)
            flash (ret["message"], category=ret["category"])
            flash ("evtl. geänderte Config muss geöffnet werden.", category="warning")
        else:
            flash (f"Restore: kein USB Laufwerk angegeben.", category="danger")
        return "ok"

    if "usbdrive"  in session: 
        mappath = globs.room.usbmap().replace (os.sep, '+')
    else: # als Backup, falls forms.usb (restore) schiefläuft.
        mappath = globs.room.rootpath().replace (os.sep, '+')
    
    session.pop ("usbcheck", None)

    ret ={}
    ret["spath"] = mappath
    ret["updir"] = "true"
    ret["dialogbox"] = render_template ("modaldialog.html", body="filedialog",
                       title = "Backup wählen")
    return json.dumps (ret)


@room.route ("/headupdate")
@admin_required
def headupdate ():
    """ geänderte Heads in codepath schreiben
    """
    globs.room.headupdate ()
    flash ("Heads update ok", category="success")
    return redirect (redirect_url ())


@room.route ("/del_unusedcues")
@admin_required
def del_unusedcues ():
    """ unbenutzte Cues löschen """
    ret = globs.room.remove_unused_cues ()
    flash (ret["message"], category=ret["category"])
    return redirect (redirect_url ())


@room.route ("/save_changes")
@admin_required
def save_changes ():
    """ alle Änderungen in csv-Dateien speichern """
    ret = globs.room.save_changes ()
    flash (ret["message"], category=ret["category"])
    return redirect (redirect_url ())


@room.route ("/discard_changes")
@standarduser_required
def discard_changes ():
    """ alle Änderungen in csv-Dateien verwerfen """
    ret = globs.room.discard_changes ()
    if ret["count"] != 0:
        load_config () # config neu laden.
    flash (ret["message"], category=ret["category"])
    return redirect (redirect_url ())


@room.route ("/make_archive")
@standarduser_required
def make_archive ():
    """ ZIP-Archiv des aktuellen Raums erzeugen und download
    """
    ret = globs.room.make_archive ()
    # zipfile in UPLOAD_FOLDER verschieben:
    zipfile = ret["zipfile"]
    zippath, filename = os.path.split (zipfile)
    dst = os.path.join (current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.isfile (dst): # dst existiert
        os.remove (dst)
    shutil.move (zipfile, dst)
    flash (f"Archiv {filename} wurde erzeugt.", category="success")
    
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)
