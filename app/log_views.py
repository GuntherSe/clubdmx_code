#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import imp
import os
import os.path
import json

from flask import Blueprint, render_template, request, json #, redirect
from flask import session, flash #, url_for, send_from_directory
#from flask import current_app
from flask_login import login_required

import logging
from loggingbase import readlogfile

from apputils import standarduser_required #, admin_required, redirect_url

import globs

logbp = Blueprint ("logbp", __name__, url_prefix="", 
                  static_folder="static", template_folder="templates")


@logbp.route ("/logview")
@login_required
@standarduser_required
def logview ():
    """ Logfile anzeigen 
    """
    logdir = os.path.join (globs.basedir, "logs")
    logdir = logdir.replace (os.sep, '+')
    return render_template ("logview.html", logdir=logdir)


@logbp.route ("/getlogfile")
def getlogfile () ->json:
    """ Logfile  in HTML 

    return im JSON-Format
    """
    # aktuell angezeigtes logfile in session speichern:
    fullname = request.args.get ("name")
    filterstr = request.args.get ("filter")

    if fullname != "" and fullname != "undefined":
        session["logname"] = fullname
    else:
        if "logname" in session:
            fullname = session["logname"]
        else:
            return "kein Logfile ausgewählt."
    
    fullname = fullname.replace ('+', os.sep) # '+' in '/' umwandeln
    path, shortname = os.path.split (fullname)
    loglines = readlogfile (fullname, filterstr)  

    table = render_template ("logfile.html",
                    shortname = shortname, 
                    fullname = fullname,
                    lines = loglines)
    return json.dumps (table)

@logbp.route ("/delete_log", methods = ["GET","POST"])
@login_required
@standarduser_required
def delete_log ():
    """ File löschen nach Bestätigung 
    
    siehe bascic_views - delete_csv
    """
    if request.method == 'POST':
        # Filename ist in session gespeichert
        # args = json.loads (request.form["args"])
        if "deletefile" in session:
            fullname = session["deletefile"]
            session.pop ("deletefile")
            session.pop ("logname", None) 
            fullname    = fullname.replace ('+', os.sep)
            path, shortname = os.path.split (fullname)
            os.remove (fullname)
            flash (f"Datei '{shortname}' wurde gelöscht.")
        return "ok"
    
    if "filename" in request.args:
        filename = request.args.get ("filename")
        if filename == "": # Dateiname in session gespeichert
            if "logname" in session:
                filename = session["logname"]
            else:
                filename = None

    if filename:
        session["deletefile"] = filename
        fullname = filename.replace ('+', os.sep) # '+' in '/' umwandeln
        path, shortname = os.path.split (fullname)

        text = f"Soll die Datei '{shortname}' gelöscht werden?"
        title = "Löschen bestätigen"
    else:
        session.pop ("deletefile", None)
        text = f"keine Datei zum Löschen ausgewählt"
        title = "Löschen bestätigen"

    
    return render_template ("modaldialog.html", title = title,
                                            body  = "confirmbody",
                                            text = text,
                                            submit_text = "löschen")

