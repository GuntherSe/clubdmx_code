#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Views zu class Csvfile """

import os
import os.path
import csv

from flask import Blueprint, render_template, request, json, redirect 
from flask import flash, session
from flask_login import login_required
from apputils import standarduser_required, admin_required, redirect_url
# from common_views import check_clipboard

import globs

from cue import Cue
from csvfileclass import Csvfile   
from cuebutton import Cuebutton
from startup import load_config
from midiutils import get_midicommandlist
# from startup_levels import fader_locations, button_locations
from startup_func import make_cuelistpages, make_fadertable, make_cuebuttons

csvview = Blueprint ("csvview", __name__, url_prefix="/csv", 
                     static_folder="static", template_folder="templates")

# --- evaluate_option ---------------------------------------------------------
def evaluate_option (option:str):
    """ beim Ändern von diversen Tabellen globals aktualisieren 
    option: Verzeichnis der csv-Tabellen
    """

    if option == "patch":
        globs.patch.reload ()
        make_fadertable ()
        make_cuebuttons ()
    elif option == "config":
        load_config (with_currentlevels=True)
    elif option == "cuefader":
        make_fadertable ()
    # cue: automatisches Update, wenn level == 0
    elif option == "head":
        globs.patch.reload ()
        make_fadertable ()
        make_cuebuttons ()
    elif option == "midibutton":
        # print ("Midibuttons neu einlesen.")
        get_midicommandlist ()
    elif option == "cuebutton":
        make_cuebuttons ()
    elif option == "pages":
        make_cuelistpages ()
    # cuelist: automatisches Update (level==0, Pause oder fading-done)
    elif option == "layout":
        globs.room.layout.__init__ ("layout")

@csvview.route ("/save")
@admin_required
def save_changes () :
    """ Änderungen der Csv-Tabelle sichern, ccsv entfernen 
    return: Redirect-Url
    """
    fname = request.args.get ("name")
    fname = fname.replace ('+', os.sep)
    # option = request.args.get ("option")
    csvfile = Csvfile (fname)
    if csvfile.save_changes ():
        flash ("Änderungen gesichert.", category="success")
    else:
        flash ("Keine Änderungen zu sichern.", category="info")

    return redirect (redirect_url())

@csvview.route ("/discard")
def discard_changes () :
    """ Änderungen der Csv-Tabelle verwerfen, ccsv entfernen 
    return: Reditect-Url
    """
    fname = request.args.get ("name")
    fname = fname.replace ('+', os.sep)
    option = request.args.get ("option")
    csvfile = Csvfile (fname)
    if csvfile.discard_changes ():
        evaluate_option (option)
        flash ("Änderungen verworfen.", category="success")
    else:
        flash ("keine Änderungen vorhanden",  category="info")

    return redirect (redirect_url())

@csvview.route ("/savecell", methods = ["POST"])
def save_cell():
    """ CSV-Zelle speichern
    option = subdir von globs.room
    """
    fname    = request.form["file"]
    fname    = fname.replace ('+', os.sep)
    row_num  = request.form["row_num"]
    col_num  = request.form["col_num"]
    text     = request.form["text"]
    try:
        option   = request.form["option"]
    except:
        option = None

    csvfile = Csvfile (fname)
    if option:
        # prüfen ob text layout-konform ist:
        fieldnames = csvfile.fieldnames ()
        field = fieldnames[int(col_num)-1]
        chk = globs.room.layout.check (option+field.lower() , text)
        if chk == False:
            flash (f"'{text}' passt nicht ins Feld '{field}'.", 
                category="danger")
            return "error"

    ret = csvfile.write_cell (row_num, col_num, chk)
    if ret["tablechanged"] == "true":
        evaluate_option (option)
    return "ok"


@csvview.route ("/filename", methods = ["GET","POST"])
def filename():
    """ CSV-Zelle mit File-Informationen speichern, 
    infos von JS:filedialogToPython
    """
    if request.method == 'POST':
        args = json.loads (request.form["args"])
        fname    = args["file"]
        fname    = fname.replace ('+', os.sep)
        row_num  = args["row_num"]
        col_num  = args["col_num"]
        option   = args["option"]
        text     = request.form["shortname"]

        csvfile = Csvfile (fname)
        ret = csvfile.write_cell (row_num, col_num, text)
        
        # evaluate_option für Liste auswählen, die File enthält
        # zB cuebutton enthält cue, daher evaluate_option für cuebutton
        direc = os.path.dirname (fname)
        root, subdir = os.path.split (direc)
        if (ret["tablechanged"] == "true"):
            evaluate_option (subdir)
            # flash (ret["message"], category=ret["category"])
        return "ok" #json.dumps (ret)

    option = request.args.get ("option")

    ret = {}
    ret["spath"] = option
    ret["dialogbox"] = render_template ("modaldialog.html", body="filedialog")
    ret["ftype"] = ".csv"
    return json.dumps (ret)


@csvview.route ("/open", methods= ["GET","POST"])
@login_required
def open ():
# Button "Öffnen":
    if request.method == 'POST':
        # Filename:
        path = request.form["path"]
        path = path.replace ('+', os.sep) # '+' in '/' umwandeln
        filename = request.form["filename"]
        fileroot, fileext  = os.path.splitext (filename )
        fullname = path + os.sep + filename
        args = json.loads (request.form["args"])
        option = args["option"]

        if option == "config": #config neu laden
            globs.cfgbase.set ("config", fileroot) # in app.csv schreiben
            globs.cfgbase.save_data()
            globs.cfg.open (fullname)
            # config neu laden:
            load_config ()
            flash ("Konfiguration geladen.", category="success")
            return "ok"

        if option == "cuefader": 
            # Cueinfotabelle ausgewählt
            loc = args["location"]
            globs.cfg.set (loc, fileroot)
            globs.cfg.save_data ()
            make_fadertable ()
            flash ("Fader-Tabelle geladen.", category="success")
            return "ok"

        if option == "cuebutton":
            loc = args["location"]
            globs.cfg.set (loc, fileroot)
            globs.cfg.save_data ()
            make_cuebuttons ()
            flash ("Button-Tabelle geladen.", category="success")
            return "ok"

        if option == "stage": # siehe stage.py und stage.html
            session ["stagename"] = fileroot
            # globs.cfg.set ("stage", fileroot)
            # globs.cfg.save_data ()
            return "ok"

        if option == "patch": # patchtabelle ausgewählt
            # current = globs.cfg.get ("patch")
            ret = globs.patch.open (fileroot) # False bei Fehler in Headfiles
            if ret["category"] == "success":
                globs.cfg.set ("patch", fileroot)
                globs.cfg.save_data()
            flash (ret["message"], category=ret["category"])
            return "ok"

        if option == "cuelist": # cuelist ausgewählt
            session["selected_cuelist"] = fileroot
            # session["open_requested"] = True
            return "ok"
        
        if option == "pages": # cuelist Pages
            session.pop ("selected_cuelist", None)
            globs.cfg.set ("pages", fileroot)
            globs.cfg.save_data ()
            for item in globs.cltable:
                item.level = 0
            make_cuelistpages ()
            flash ("Cuelisten-Tabelle geladen.", category="success")

        if option == "midibutton":
            flash (f"Midibuttons ausgewählt: {fileroot}")
            globs.cfg.set ("midi_buttons", fileroot)
            globs.cfg.save_data ()
            get_midicommandlist ()

            return "ok"
        # unbekannte option:
        return "ok"

    ret = {}
    ret["spath"] = request.args.get ("option")
    ret["dialogbox"] = render_template ("modaldialog.html", body="filedialog")
    ret["ftype"] = ".csv"
    return json.dumps (ret)


@csvview.route ("/saveas", methods= ["GET","POST"])
def saveas ():
    """  Button 'sichern als' 

    kann von einer Config-Seite oder von den Datenbank-Seiten kommen.
    Config: 'option' wird  in request.form['args'] gesetzt
            'option' ist gleichzeitig 'spath' (Subdir)
    Datenbank: 'option' nicht gesetzt.
               'spath' muss in request.form['args'] sein
    """
    if request.method == 'POST':
        # Filename:
        path = request.form["path"]
        path = path.replace ('+', os.sep) # '+' in '/' umwandeln
        filename = request.form["filename"]
        filename = filename.replace ('+', '_') # kein '+' im Namen
        fileroot, fileext  = os.path.splitext (filename )
        fullname = os.path.join (path, fileroot)
        args = json.loads (request.form["args"])

        if "spath" in args: # aufgerufen von der Datenbank
            # aktuell angezeigte Tabelle
            spath = args["spath"]
            storename = "visible" + spath
            current = session[storename]
            current = current.replace ('+', os.sep)

            basecsv = Csvfile (current)
            ret = basecsv.backup (fullname)
            session[storename] = fullname
            flash (ret["message"], category=ret["category"])
            return "ok"

        option = args["option"]
        # Basefile = Ursprungs-File:
        if option == "config":
            current = globs.cfg.file.name ()
            basecsv = Csvfile (current)
            ret = basecsv.backup (fullname)
            globs.cfg.open (fullname)

        elif option == "cuefader": # fadertabelle ausgewählt
            loc = args["location"]
            current = globs.cfg.get (loc) # "cuefaders")
            csvfile = Csvfile (os.path.join (globs.room.cuefaderpath(), current))
            ret = csvfile.backup (fullname)
            globs.cfg.set (loc, fileroot)
            globs.cfg.save_data ()
            make_fadertable () #   fileroot)

        elif option == "cuebutton": # Cueinfotabelle ausgewählt
            loc = args["location"]
            current = globs.cfg.get(loc)
            csvfile = Csvfile (os.path.join (globs.room.cuebuttonpath(), current))
            ret = csvfile.backup (fullname)
            globs.cfg.set (loc, fileroot)
            globs.cfg.save_data ()
            make_cuebuttons ()

        elif option == "patch": # patchtabelle ausgewählt
            current = globs.patch.file.name ()
            basecsv = Csvfile (current)
            ret = basecsv.backup (fullname)
            globs.patch.open (fileroot) # False bei Fehler in Headfiles
            globs.cfg.set ("patch", fileroot)
            globs.cfg.save_data()

        elif option == "midibutton": # Tebelle midibuttons ausgewählt
            current = globs.cfg.get ("midi_buttons")
            basecsv = Csvfile (os.path.join (globs.room.midibuttonpath(), current))
            ret = basecsv.backup (fullname)
            globs.cfg.set ("midi_buttons", fileroot)
            globs.cfg.save_data()

        elif option == "stage":
            if "stagename" in session:
                current = session["stagename"]
            else:
                current = globs.cfg.get ("stage") 
            csvfile = Csvfile (os.path.join (globs.room.stagepath(), current))
            ret = csvfile.backup (fullname)
            globs.cfg.set ("stage", fileroot)
            globs.cfg.save_data ()
            session["stagename"] = fileroot

        elif option == "cuelist":
            if "selected_cuelist" in session:
                current = session["selected_cuelist"]
            else:
                current = "_neu" 
            csvfile = Csvfile (os.path.join (globs.room.cuelistpath(), current))
            ret = csvfile.backup (fullname)
            session["selected_cuelist"] = fileroot

        elif option == "pages":
            current = globs.cfg.get ("pages")
            csvfile = Csvfile (os.path.join (globs.room.pagespath(), current))
            ret = csvfile.backup (fullname)
            globs.cfg.set ("pages", fileroot)
            globs.cfg.save_data ()

        flash (ret["message"], category=ret["category"])
        return "ok"

    ret = {}
    if "spath" in request.args:
        ret["spath"] = request.args.get ("spath")
    else:
        ret["spath"] = request.args.get ("option")
    ret["ftype"] = ".csv"
    ret["dialogbox"] = render_template ("modaldialog.html", body = "filedialog",
                                        title = "sichern als")
    return json.dumps (ret)


@csvview.route ("/rename", methods= ["GET","POST"])
def rename ():
    """  Button 'renmae' 

    kann von einer Config-Seite oder von den Datenbank-Seiten kommen.
    Config: 'option' wird  in request.form['args'] gesetzt
            'option' ist gleichzeitig 'spath' (Subdir)
    Datenbank: 'option' nicht gesetzt.
               'spath' muss in request.form['args'] sein
    """
    if request.method == 'POST':
        newname = request.form ["name"]
        # Filename:
        # path = request.form["path"]
        # path = path.replace ('+', os.sep) # '+' in '/' umwandeln
        # filename = request.form["filename"]
        # filename = filename.replace ('+', '_') # kein '+' im Namen
        # fileroot, fileext  = os.path.splitext (filename )
        # fullname = os.path.join (path, filename)
        args = json.loads (request.form["args"])

        # if "spath" in args: # aufgerufen von der Datenbank
        #     # aktuell angezeigte Tabelle
        #     spath = args["spath"]
        #     storename = "visible" + spath
        #     current = session[storename]
        #     current = current.replace ('+', os.sep)

        #     basecsv = Csvfile (current)
        #     ret = basecsv.backup (fullname)
        #     session[storename] = fullname
        #     flash (ret["message"], category=ret["category"])
        #     return "ok"

        if "option" not in args:
            flash ("'option' nicht angegeben.")
            return "not ok"

        option = args["option"]
        # Basefile = Ursprungs-File:
        if option == "config":
            current = globs.cfg.file.name ()
            basecsv = Csvfile (current)
            basecsv.rename (newname)
            globs.cfgbase.set ("config", newname)
            globs.cfgbase.save_data ()
            fullname = os.path.join (basecsv.path(), newname)
            globs.cfg.file.name (fullname)
            globs.cfg.save_data ()
            flash (f"Config in {newname} umbenannt.")
            return "ok"

        # elif option == "cuefader": # Cueinfotabelle ausgewählt
        #     current = globs.cfg.get("cuefaders")
        #     csvfile = Csvfile (os.path.join (globs.room.cuefaderpath(), current))
        #     ret = csvfile.backup (fullname)
        #     make_fadertable (fileroot)
        #     globs.cfg.set ("cuefaders", fileroot)
        #     globs.cfg.save_data ()

        # elif option == "cuebutton": # Cueinfotabelle ausgewählt
        #     current = globs.cfg.get("cuebuttons")
        #     csvfile = Csvfile (os.path.join (globs.room.cuebuttonpath(), current))
        #     ret = csvfile.backup (fullname)
        #     make_cuebuttons (fileroot)
        #     globs.cfg.set ("cuebuttons", fileroot)
        #     globs.cfg.save_data ()

        # elif option == "patch": # patchtabelle ausgewählt
        #     current = globs.patch.file.name ()
        #     basecsv = Csvfile (current)
        #     ret = basecsv.backup (fullname)
        #     globs.patch.open (fileroot) # False bei Fehler in Headfiles
        #     globs.cfg.set ("patch", fileroot)
        #     globs.cfg.save_data()

        # elif option == "stage":
        #     current = globs.cfg.get ("stage") 
        #     csvfile = Csvfile (os.path.join (globs.room.stagepath(), current))
        #     ret = csvfile.backup (fullname)
        #     globs.cfg.set ("stage", fileroot)
        #     globs.cfg.save_data ()

        # flash (ret["message"], category=ret["category"])
        # return "ok"

    if "spath" in request.args:
        subdir = request.args.get ("spath") # Datenbank
    else:
        subdir = request.args.get ("option") # eine Config-Seite
    return render_template ("modaldialog.html", 
                                body = "stringbody",
                                text = "neuen Namen eingeben",
                                submit_text = "umbenennen",
                                title = f"{subdir}-Datei umbenennen")


@csvview.route ("/sort")
def sort ():
    """ csv File nach Feld sortieren
    
    siehe cl-editor.html
    """
    fname = request.args.get ("name")
    pluspath = request.args.get ("pluspath")
    pluspath = pluspath.replace ('+', os.sep)
    fullname = os.path.join (pluspath, fname)
    csvfile = Csvfile (fullname)
    field = request.args.get ("field")

    ret = csvfile.sort (field)
    flash (ret["message"], category=ret["category"])
    return "ok"
