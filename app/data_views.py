#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import csv

from flask import Blueprint, render_template, request, json, redirect
from flask import session #, url_for
from flask_login import login_required
from apputils import standarduser_required
from common_views import check_clipboard

import globs

from csvfileclass import Csvfile
from ola import get_ip_address
from filedialog_util  import dir_explore 

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

    excludebuttons = ["openButton", "saveasButton", "uploadButton"]
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


