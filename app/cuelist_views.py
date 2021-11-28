#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Views zu class Cuelist """

import os
import os.path
import csv

from flask import Blueprint, render_template, request, json 
from flask import flash, session
# from flask_login import login_required
# from apputils import standarduser_required, admin_required, redirect_url
# from common_views import check_clipboard

import globs

from cue import Cue
from csvfileclass import Csvfile   
from cuelist import Cuelist
# from startup_levels import cuelist_locations
# from cuebutton import Cuebutton
# from startup_func import make_fadertable, get_cuebuttons
# from csv_views import evaluate_option

clview = Blueprint ("cuelist", __name__, url_prefix="/cuelist", 
                     static_folder="static", template_folder="templates")


def get_cldata () -> dict:
    """ Daten aus global.cltable 
    
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
    if csvfile.changed():
        data["changes"] = "true"
    else:
        data["changes"] = "false"

    if len (data["items"]):
        found_data = "true"
    data["found_data"] = found_data
    return data


# --- cuelist Viewfunktionen ------------------------------------------------

@clview.route ("/faderpage")
def faderpage () ->json: 
    """ Fader-Seite: pro Cuelist ein level-Fader und Bedienbuttons
    
    """
    data = get_cldata ()
    
    if data["found_data"] == "false":
        flash ("Es sind noch keine Cuelisten vorhanden.")

    return render_template ("cl-faderpage.html", data=data)


@clview.route ("/status")
def status () ->json:
    """ Cuelist Status """
    ret = {}
    num_cl = len (globs.cltable)
    levels = [int (globs.cltable[i].level *255) for i in range (num_cl)]
    ret["levels"] = levels
    status = [globs.cltable[i].status () for i in range (num_cl)]
    ret["status"] = status
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
