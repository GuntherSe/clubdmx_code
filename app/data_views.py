#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import csv

from flask import Blueprint, render_template, request, json, redirect
from flask import session, flash #, url_for
from flask_login import login_required
from apputils import standarduser_required, admin_required, redirect_url
from common_views import check_clipboard

import globs

from csvfileclass import Csvfile
from ola import get_ip_address
from filedialog_util  import dir_explore 
from stage import get_stage_filename
from startup import load_config

data = Blueprint ("data", __name__, url_prefix="", 
                  static_folder="static", template_folder="templates")


@data.route ("/patch")
@login_required
@standarduser_required
def patch ():
    csvfile = Csvfile (globs.patch.file.name())
    if csvfile.changed():
        changes = "true"
    else:
        changes = "false"
    check_clipboard ()

    return render_template ("patch.html", shortname = csvfile.shortname(),
                            pluspath = csvfile.pluspath(),
                            fieldnames = csvfile.fieldnames(),
                            items = csvfile.to_dictlist(), 
                            option  = "patch",
                            changes = changes,
                            filebuttons = "false",
                            excludebuttons = [] )

# -- Datenbank ----------------------------------------------------------------


# @data.route ("/dataedit/<path>")
# @login_required
# def dataedit (path:str):
#     return render_template ("data/dataedit.html", spath=path)

@data.route ("/dataedit_config")
@login_required
@standarduser_required
def dataedit_config ():
    return render_template ("data/dataedit.html", spath="config")

@data.route ("/dataedit_cue")
@login_required
@standarduser_required
def dataedit_cue ():
    return render_template ("data/dataedit.html", spath="cue")

@data.route ("/dataedit_cuebutton")
@login_required
@standarduser_required
def dataedit_cuebutton ():
    return render_template ("data/dataedit.html", spath="cuebutton")

@data.route ("/dataedit_cuelist")
@login_required
@standarduser_required
def dataedit_cuelist ():
    return render_template ("data/dataedit.html", spath="cuelist")

@data.route ("/dataedit_pages")
@login_required
@standarduser_required
def dataedit_pages ():
    return render_template ("data/dataedit.html", spath="pages")

@data.route ("/dataedit_patch")
@login_required
@standarduser_required
def dataedit_patch ():
    return render_template ("data/dataedit.html", spath="patch")

@data.route ("/dataedit_cuefader")
@login_required
@standarduser_required
def dataedit_cuefader ():
    return render_template ("data/dataedit.html", spath="cuefader")

@data.route ("/dataedit_head")
@login_required
@standarduser_required
def dataedit_head ():
    return render_template ("data/dataedit.html", spath="head")

@data.route ("/dataedit_midibutton")
@login_required
@standarduser_required
def dataedit_midibutton ():
    return render_template ("data/dataedit.html", spath="midibutton")

@data.route ("/dataedit_stage")
@login_required
@standarduser_required
def dataedit_stage ():
    history = request.args.get ("history") # für Rücksprung
    if history:
        session["history"] = history
    else:
        session.pop ("history", None)

    return render_template ("data/dataedit.html", spath="stage")

@data.route ("/ola")
def ola ():
    ola_ip = globs.cfg.get("ola_ip")
    if ola_ip == "localhost" or ola_ip == "127.0.0.1":
        ola_ip = get_ip_address()
    return redirect ("http://" + ola_ip + ":9090/ola.html")


@data.route ("/dblayout")
@login_required
@standarduser_required
def dblayout ():
    """ Datenbank-Layout in Tabelle anzeigen
    """
    csvfile = globs.room.layout 
    if csvfile.changed():
        changes = "true"
    else:
        changes = "false"

    excludebuttons = ["openButton", "saveasButton", "uploadButton", "deleteButton"]
    return render_template ("data/dblayout.html",
                    shortname  = csvfile.shortname(),
                    pluspath   = csvfile.pluspath(),
                    fieldnames = csvfile.fieldnames(),
                    items      = csvfile.to_dictlist(),
                    option     = "layout",
                    changes    = changes,
                    style      = "table-sm table-striped table-responsive",
                    filebuttons = "false", 
                    excludebuttons = excludebuttons )


@data.route ("/gettable")
def gettable () ->json:
    """ Tabelle  in HTML 

    verwendet in Datenbank-Modulen
    """
    # aktuell angezeigte Tabelle in session speichern:
    fullname = request.args.get ("name")
    option   = request.args.get ("option")
    if option:
        storename = "visible"+option
    else:
        return "keine Option gewählt."

    if fullname != "" and fullname != "undefined+undefined":
        session[storename] = fullname
    elif storename == "visiblestage":
        # Sprung von Stage_view
        fullname = get_stage_filename ()
    else:
        if storename in session:
            fullname = session[storename]
        else:
            return "keine Tabelle ausgewählt."
    
    fullname = fullname.replace ('+', os.sep) # '+' in '/' umwandeln
    csvfile = Csvfile (fullname)
    if csvfile.changed():
        changes = "true"
    else:
        changes = "false"

    # Clipboard enthält Daten?
    check_clipboard ()

    excludebuttons = ["openButton"]

    table = render_template ("csvtable.html", 
                    shortname  = csvfile.shortname(),
                    pluspath   = csvfile.pluspath(),
                    fieldnames = csvfile.fieldnames(),
                    items      = csvfile.to_dictlist(),
                    changes    = changes,
                    excludebuttons = excludebuttons,
                    filebuttons = "false",
                    option     = option)
    return json.dumps (table)


@data.route ("/get_used_csv/<option>")
@login_required
@standarduser_required
def get_used_csv (option:str=""):
    return json.dumps (csv_in_use (option))



def csv_in_use (option:str="") ->list:
    """ liefert Liste der verwendeten csv-Dateien
    
    option: nur dieses Verzeichnis (=subdir) durchsuchen
    wenn option == "", dann liste aller verwendeten csv-Dateien
    return: list of tuples [subdir, filename ohne extension]
    """
    ret = []
    # structure for ret: [subdir:str,filename without ending:str]
    cfgfiles  = [["patch", globs.cfg.get ("patch")] ,
                ["cuefader", globs.cfg.get ("cuefaders")] ,
                ["cuebutton", globs.cfg.get ("cuebuttons")] ,
                ["pages", globs.cfg.get ("pages")],
                ["cue", globs.cfg.get ("startcue")],
                ["stage", globs.cfg.get ("stage")],
                ["midibutton", globs.cfg.get ("midi_buttons")],
                ["cuebutton", globs.cfg.get ("exebuttons1")],
                ["cuebutton", globs.cfg.get ("exebuttons2")] ,
                ["cuefader", globs.cfg.get ("exefaders")] ,
                ["config", globs.cfgbase.get ("config")]
                ]
    usedcues = globs.room.used_cues ()
    usedcuelists = globs.room.used_cuelists ()
    
    if option != "": 
        for item in cfgfiles:
            if item[0] == option:
                ret.append (item)
    if option == "cue":
        for item in usedcues:
            head, tail = os.path.split (item)
            ret.append (["cue", tail])
    elif option == "cuelist":
        for item in usedcuelists:
            head, tail = os.path.split (item)
            ret.append (["cuelist", tail])
    elif option == "":
        for item in cfgfiles:
            ret.append (item)
        for item in usedcues:
            head, tail = os.path.split (item)
            ret.append (["cue", tail])
        for item in usedcuelists:
            head, tail = os.path.split (item)
            ret.append (["cuelist", tail])
    elif option == "stage":
        if "stagename" in session:
            ret.append (["stage", session["stagename"]])

    return ret


# --- fileDialog -----------------------------------------------------

@data.route ('/explore/<params>')
@login_required
def explore (params:str) -> json:
    """ Dir Content: Bootstrap Liste und aktuelles Verzeichnis:str

    an JS Callback schicken
    """
    return dir_explore (params)


@data.route ("/filedialogbox")
@login_required
def filedialogbox ():
    title =   request.args.get ("title")
    ftype =   request.args.get ("ftype")
    submit_text = request.args.get ("submit_text")
    ret = render_template ("modaldialog.html", body = "filedialog",
                                title = title,
                                ftype = ftype,
                                submit_text = submit_text)
    return json.dumps (ret)


@data.route ("/delete_csv", methods = ["GET","POST"])
@login_required
@admin_required
def delete_csv ():
    """ File löschen nach Bestätigung 
    
    Ablauf ähnlich wie bei /csv/saveas
    """
    if request.method == 'POST':
        # Filename ist in session gespeichert
        args = json.loads (request.form["args"])
        loc = "visible" + args["spath"]
        if "deletefile" in session:
            fname = session["deletefile"]
            if loc == fname:
                session.pop (loc, None)
            session.pop ("deletefile")
            fname    = fname.replace ('+', os.sep)
            csvfile = Csvfile (fname)
            # _neu kann nicht gelöscht werden:
            shortname = csvfile.shortname()
            if shortname == "_neu":
                flash ("Diese Datei kann nicht gelöscht werden.")
                return "ok"
            csvfile.remove ()
            # bei csv-in-use: load_config
            used = csv_in_use (args["spath"])
            if len (used):
                for item in used:
                    if item[1] == shortname:
                        load_config (with_currentlevels=True)
                        # Spezialfall Cuelist:
                        if args["spath"] == "cuelist":
                            flash (f"Die Cueliste '{shortname}' wurde geleert.")
                            return "ok"
            flash (f"Datei '{shortname}' wurde gelöscht.")
        return "ok"
    
    if "filename" in request.args and "spath" in request.args:
        filename = request.args.get ("filename")
        if filename == "": # Dateiname in session gespeichert
            loc = "visible" + request.args.get ("spath")
            if loc in session:
                filename = session[loc]
            else:
                filename = None

    if filename:
        session["deletefile"] = filename
        fullname = filename.replace ('+', os.sep) # '+' in '/' umwandeln
        csvfile = Csvfile (fullname)

        text = f"Soll die Datei '{csvfile.shortname()}' gelöscht werden?"
        title = "Löschen bestätigen"
    else:
        session.pop ("deletefile", None)
        text = f"keine Datei zum Löschen ausgewählt"
        title = "Löschen bestätigen"

    
    return render_template ("modaldialog.html", title = title,
                                            body  = "confirmbody",
                                            text = text,
                                            submit_text = "löschen")

