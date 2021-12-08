#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Views zu class Cuelist """

import os
import os.path

from flask import Blueprint, render_template, request, json 
from flask import flash, session
from flask_login import login_required
from apputils import standarduser_required, admin_required, redirect_url
from common_views import check_clipboard

import globs

# from cue import Cue
from csvfileclass import Csvfile   
from cuelist import Cuelist
# from room_views import new
# from startup_levels import cuelist_locations
# from cuebutton import Cuebutton
# from csv_views import evaluate_option

clview = Blueprint ("cuelist", __name__, url_prefix="/cuelist", 
                     static_folder="static", template_folder="templates")


def get_cldata () -> dict:
    """ Daten zu allen Cuelisten, aus global.cltable 
    
    data: { "cldata" : {"fieldname1":"val1", "fieldname2":"val2", ... }
            "found_data" : "true" oder "false"
    }
    """
    data = {}
    found_data = "false"
    # wenn cuelists in verschiedenen locations vokommen, dann hier erweitern

    fname = globs.cfg.get("pages")
    filename = os.path.join (globs.room.pagespath(),fname)
    csvfile = Csvfile (filename)
    # ft = list (csvfile.fieldnames())
    data["shortname"]  = fname
    data["pluspath"]   = csvfile.pluspath ()
    data["fieldnames"] = [x for x in csvfile.fieldnames()]
    # _fieldnames sind geschützt
    data["option"]     = "pages"
    data["items"]      = Cuelist.items ()
    data["textcolumn"] = csvfile.fieldnames().index("Text")
    data["filebuttons"] = "cuelist"
    if csvfile.changed():
        data["changes"] = "true"
    else:
        data["changes"] = "false"

    if len (data["items"]):
        found_data = "true"
    data["found_data"] = found_data
    return data


def reload_cuelist (args:dict):
    """ cueliste neu laden:
    wenn Änderungen gepeichert wurden oder pages-Seite geändert wurde
    siehe evaluate_option in csv_views.py
    filename: geänderte page
    row_num: Filename in Zeile row_num geändert, Zählung ab 1
    """
    pass

# --- cuelist Viewfunktionen ------------------------------------------------

@clview.route ("/pages")
def pages () ->json: 
    """ Cuelist-Seite: pro Cuelist ein level-Fader und Bedienbuttons
    
    """
    data = get_cldata ()
    
    if data["found_data"] == "false":
        flash ("Es sind noch keine Cuelisten vorhanden.")

    return render_template ("cl-pages.html", data=data)


@clview.route ("/pagessetup")
def pagessetup () -> json:
    """ Pages-Seite einrichten/bearbeiten 
    """
    check_clipboard ()

    # Daten von der csv-Datei holen:                            
    fname = globs.cfg.get("pages")
    filename = os.path.join (globs.room.pagespath(),fname)
    csvfile = Csvfile (filename)
    if csvfile.changed():
        changes = "true"
    else:
        changes = "false"

    return render_template ("cl-pages-setup.html", 
                    shortname = csvfile.shortname(),
                    pluspath = csvfile.pluspath(),
                    fieldnames = csvfile.fieldnames(),
                    items = csvfile.to_dictlist(), 
                    changes = changes,
                    option  = "pages", 
                    filebuttons = "cuelist",
                    excludebuttons = [] )


@clview.route ("/editor")
@clview.route ("/editor/<name>")
@login_required
@standarduser_required
def editor (name:str = "") ->json: 
    """ Editor für Cueliste 
    fname: Name der zuletzt editierten Cuelist
    index: editor wurde über Button von cl-pages.html aufgerufen. 
        Status-Fenster wird angezeigt.
    """
    # index: Wenn vorhanden, dann kommt der Aufruf von cl-pages
    index = request.args.get ("index")
    if index:
        excludebuttons = ["openButton", "saveasButton"]
    else:
        excludebuttons = []
        index = ""

    # Name:
    filename = request.args.get ("filename")
    if filename:
        name = filename
        session["selected_cuelist"] = name
    # if "open_requested" in session and session["open_requested"] == True: 
    #     # open-Button hat editor neu geladen.
    #     session.pop ("open_requested")
    #     name = session["selected_cuelist"]
    #     index = ""
    elif name:
        session["selected_cuelist"] = name
    elif "selected_cuelist" in session:
        name = session["selected_cuelist"]
    else:
        name = "_neu"
    
    filename = os.path.join (globs.room.cuelistpath(),name)
    csvfile = Csvfile (filename)
    if csvfile.changed():
        changes = "true"
    else:
        changes = "false"
    
    check_clipboard ()

    return render_template ("cl-editor.html", 
                            shortname = csvfile.shortname(),
                            pluspath = csvfile.pluspath(),
                            fieldnames = csvfile.fieldnames(),
                            items = csvfile.to_dictlist(), 
                            option  = "cuelist",
                            changes = changes,
                            filebuttons = "cue",
                            index = index,
                            excludebuttons = excludebuttons )
  

# --- Hilfsfunktionen -------------------------------------------------------

@clview.route ("/allstatus")
def allstatus () ->json:
    """ Status aller Cuelisten"""
    ret = {}
    num_cl = len (globs.cltable)
    levels = [int (globs.cltable[i].level *255) for i in range (num_cl)]
    ret["levels"] = levels
    status = [globs.cltable[i].status () for i in range (num_cl)]
    ret["status"] = status
    return json.dumps (ret)


@clview.route ("/status/<index>")
def status (index:str) ->json:
    """ Status der Cuelist mit Index 'index' 
    
    index: index in Cuelist.instances
    """
    ret = {}
    idx = int (index)
    if idx in range (len (globs.cltable)):
        ret["level"]  = int (globs.cltable[idx].level *255) 
        ret["status"] = globs.cltable[idx].status ()

    return json.dumps (ret)


@clview.route ("/go")
def go () -> str:
    """ Go-Button drücken """
    butt = request.args.get ("index")
    index = int(butt)
    if index in range (len (globs.cltable)):
        globs.cltable[index].go ()
    return "ok"


@clview.route ("/pause")
def pause () -> str:
    """ Pause-Button drücken """
    butt = request.args.get ("index")
    index = int(butt)
    if index in range (len (globs.cltable)):
        globs.cltable[index].pause ()
    return "ok"


@clview.route ("/minus")
def minus () -> str:
    """ Minus-Button """
    butt = request.args.get ("index")
    index = int(butt)
    if index in range (len (globs.cltable)):
        globs.cltable[index].decrement_nextprep ()
    return "ok"


@clview.route ("/plus")
def plus () -> str:
    """ Plus-Button """
    butt = request.args.get ("index")
    index = int(butt)
    if index in range (len (globs.cltable)):
        globs.cltable[index].increment_nextprep ()
    return "ok"


@clview.route ("/coledit",  methods = ["GET", "POST"])
def coledit () -> str:
    """ Spalten editieren """
    if request.method == 'POST':
        newval = request.form["newval"]
        fname  = request.form["file"]
        fname  = fname.replace ('+', os.sep)
        option = request.form["option"] 
        field  = request.form["field"]
        col_num  = request.form["col_num"]
        # neuen Wert prüfen:
        chk = globs.room.layout.check (option+field.lower() , newval)
        if chk == False:
            flash (f"'{newval}' passt nicht ins Feld '{field}'.", 
                category="danger")
            return "error"
        # CSV-File modifizieren:
        csvfile = Csvfile (fname)
        col_num = int(col_num) -1
        ret = csvfile.col_edit (col_num, chk)
        flash (ret["message"], category=ret["category"])
        return "ok"

    field = request.args.get ("field")
    text = f"Neuer Wert für {field}:"
    return render_template ("modaldialog.html", title="Spalte editieren",
                                                text=text,
                                                body="stringbody",
                                                submit_text="OK")


@clview.route ("/details")
def details () ->json: 
    """ liefert Infos zur Cueliste 'filename'

    return: Tabelle mit Cue-Daten
    """
    filename = request.args.get ("filename")
    fullname = os.path.join (globs.room.cuelistpath (), filename)
    csvfile = Csvfile (fullname)

    excludebuttons = ["openButton", "saveasButton", "newlineButton",
                        "uploadButton", "saveChanges", "discardChanges"]
                        
    # session["editmode"] = "edit"

    table = render_template ("modaldialog.html", 
                    body = "csvbody",
                    title      = csvfile.shortname(),
                    shortname  = csvfile.shortname(),
                    pluspath   = csvfile.pluspath(),
                    fieldnames = csvfile.fieldnames(),
                    items      = csvfile.to_dictlist (),
                    excludebuttons = excludebuttons,
                    option     = "cuelist")
    return json.dumps (table)

