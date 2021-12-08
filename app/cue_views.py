#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Views zu class Cue """

import os
import os.path
import csv

from flask import Blueprint, render_template, request, json 
from flask import session
# from flask_login import login_required
# from apputils import standarduser_required, admin_required, redirect_url
from common_views import check_clipboard

import globs

from cue import Cue
from csvfileclass import Csvfile   
# from cuebutton import Cuebutton
# from startup_func import make_fadertable, get_cuebuttons
# from csv_views import evaluate_option

cueview = Blueprint ("cueview", __name__, url_prefix="/cue", 
                     static_folder="static", template_folder="templates")

# --- cue Viewfunktionen ------------------------------------------------

@cueview.route ("/cuetomodal")
def cuetomodal () ->json: 
    """ liefert Infos zum Cue 'filename'

    return: Tabelle mit Cue-Daten für Modal-Anzeige
    """
    filename = request.args.get ("filename")
    fullname = os.path.join (globs.room.cuepath (), filename)
    csvfile = Csvfile (fullname)

    excludebuttons = ["openButton", "saveasButton", "newlineButton",
                        "uploadButton", "saveChanges", "discardChanges"]
                        
    session["editmode"] = "edit"

    table = render_template ("modaldialog.html", 
                    body = "csvbody",
                    title      = csvfile.shortname(),
                    shortname  = csvfile.shortname(),
                    pluspath   = csvfile.pluspath(),
                    fieldnames = csvfile.fieldnames(),
                    items      = csvfile.to_dictlist (),
                    excludebuttons = excludebuttons,
                    option     = "cue")
    return json.dumps (table)


@cueview.route ("/cueedit", methods=['GET','POST'])
def cueedit ():
    """ cue-Editor mit Slidern

    pro Zeile in cue einen Level-Fader erzeugen,
    Änderungen an topcue senden.
    """
    if request.method == 'POST':
        head   = request.form["head"]
        attrib = request.form["attrib"]
        level  = request.form["level"]
        globs.topcue.add_item (head, attrib, level)
        # print (f"Head: {head}, Attribut: {attrib}, Level: {level}")
        return "ok"

    filename = request.args.get ("filename")
    fullname = os.path.join (globs.room.cuepath (), filename)
    tmpcue = Cue (globs.patch)
    tmpcue.open (fullname)

    ret = {}
    heads   = []
    attribs = [] # pro Zeile in Cue 'head','attrib','level'
    levels  = []
    labels  = [] # Fader-Beschriftung 
    for line in tmpcue.cuecontent():
        # in topcue eintragen:
        globs.topcue.add_item (line[0], line[1], line[2])
        heads.append (line[0])
        attribs.append (line[1])
        levels.append (int (line[2]))          # Level
        labels.append (line[0] + '-' + line[1])
    ret["heads"]   = heads
    ret["attribs"] = attribs
    ret["levels"]  = levels
    ret["table"]   = render_template ("attribslider.html", 
                                        heads=heads,
                                        attribs=attribs,
                                        labels=labels,
                                        title=filename)
    return json.dumps (ret)


@cueview.route ("/cuepage")
def cuetopage () ->json: 
    """ liefert Infos zum Cue 'filename'

    return: Seitenaufruf mit Cue-Daten für Modal-Anzeige
    """
    history = request.args.get ("history") # für Rücksprung
    if history:
        session["history"] = history
    filename = request.args.get ("filename")
    fullname = os.path.join (globs.room.cuepath (), filename)
    csvfile = Csvfile (fullname)
    if csvfile.changed():
        changes = "true"
    else:
        changes = "false"

    # Clipboard enthält Daten?
    check_clipboard ()

    excludebuttons = ["openButton"]

    return render_template ("cue.html", 
                    shortname  = csvfile.shortname(),
                    pluspath   = csvfile.pluspath(),
                    fieldnames = csvfile.fieldnames(),
                    items      = csvfile.to_dictlist(),
                    changes    = changes,
                    excludebuttons = excludebuttons,
                    filebuttons = "false",
                    option     = "cue")


