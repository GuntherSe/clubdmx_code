#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import imp
import os
import os.path
import json

from flask import Blueprint, render_template, request, json, redirect
from flask import session, flash,  url_for #, send_from_directory
from flask import current_app
from flask_login import login_required

import logging
from loggingbase import readlogfile

from cuebutton import Cuebutton

from ola import get_ip_address

from apputils import standarduser_required #, admin_required, redirect_url
from common_views import check_clipboard
from filedialog_util import dir_explore

import globs

from csvfileclass import Csvfile
from startup_levels import button_locations, fader_locations
from startup_func import fadertable_items
# from filedialog_util import list_dir


basic = Blueprint ("basic", __name__, url_prefix="", 
                  static_folder="static", template_folder="templates")

logger = logging.getLogger ("clubdmx")

# --- Hilfsfunktionen ---------------------------------------------
def get_buttondata () ->dict:
    """ Daten aus globs.buttontable, die für cuebuttons und exebuttons
    benötigt werden
    
    data:   {"cuebuttons"  : {"fieldname1":"val1", "fieldname2":"val2", ... },
             "exebuttons1" : {"fieldname1":"val1", "fieldname2":"val2", ... },
             "exebuttons2" : {"fieldname1":"val1", "fieldname2":"val2", ... },
             "found_data": "true" oder "false"
            }
    """ 
    found_data = "false"
    data = {}
    for loc in button_locations:
        data[loc] = {}
        d = data[loc]
        fname = globs.cfg.get(loc)
        filename = os.path.join (globs.room.cuebuttonpath(),fname)
        csvfile = Csvfile (filename)
        # ft = list (csvfile.fieldnames())
        d["shortname"]  = fname
        d["pluspath"]   = csvfile.pluspath ()
        d["fieldnames"] = [x for x in csvfile.fieldnames()]
        # _fieldnames sind geschützt
        d["option"]     = "cuebutton" # subdir von room
        d["loc"]        = loc # die ntsprechende Tabelle
        d["items"]      = Cuebutton.items (loc)
        d["filebuttons"] = "cue"
        # d["textcolumn"] = csvfile.fieldnames().index("Text")
        if csvfile.changed():
            d["changes"] = "true"
        else:
            d["changes"] = "false"

        if len (d["items"]):
            found_data = "true"
    data["found_data"] = found_data
    return data
        

def get_faderdata () ->dict:
    """ Daten aus globs.fadertable, die für cuefaders und exefaders
    benötigt werden
    data:   {"cuefaders" : {"fieldname1":"val1", "fieldname2":"val2", ... }, 
             "exefaders" : {"fieldname1":"val1", "fieldname2":"val2", ... },
             "found_data": "true" oder "false"
            }
    """ 
    found_data = "false"
    data = {}
    for loc in fader_locations:
        data[loc] = {}
        d = data[loc]
        fname = globs.cfg.get(loc)
        filename = os.path.join (globs.room.cuefaderpath(),fname)
        csvfile = Csvfile (filename)
        # ft = list (csvfile.fieldnames())
        d["shortname"]  = fname
        d["pluspath"]   = csvfile.pluspath ()
        d["fieldnames"] = [x for x in csvfile.fieldnames()]
        # _fieldnames sind geschützt
        d["option"]     = "cuefader"
        d["loc"]        = loc
        d["items"]      = fadertable_items (loc)
        d["textcolumn"] = csvfile.fieldnames().index("Text")
        d["filebuttons"] = "cue"
        if csvfile.changed():
            d["changes"] = "true"
        else:
            d["changes"] = "false"

        if len (d["items"]):
            found_data = "true"
    data["found_data"] = found_data
    return data
        
def list_pictures(gallery:str = "galerie"):
    """ Bilder aus /static/picture/galerie auflisten 

    alle Bilder sind jpg
    info.csv enthält die Bildnamen und die dazugehörigen Texte
    info.csv Spalten: picture,text,subtext,subtext2
    """
    
    filename = os.path.join (globs.thispath, "static", "picture", gallery, "info.csv")
    infofile = Csvfile (filename)
    pictures  = infofile.to_dictlist ()
    for pic in pictures: # Pfad ergänzen
        name = pic["picture"]
        pic["picture"] = f"picture/{gallery}/{name}"

    return pictures


# --- Basis-Seiten ------------------------------------------------

@basic.route ("/")
@basic.route ("/index")
def index ():
    room = os.path.basename (globs.room.path ())
    conffile = Csvfile (globs.cfg.file.name())
    patchfile = Csvfile (globs.patch.file.name())
    local_ip = get_ip_address ()
    pictures = list_pictures ()
    # current_app.logger.info('index aufgerufen.')

    return render_template ("index.html",
                            confname = conffile.shortname(),
                            patchname = patchfile.shortname(),
                            local_ip = local_ip,
                            ola_ip = globs.ola.ola_ip,
                            pictures = pictures,
                            room = room)


@basic.route ("/cuefader")
@login_required
def cuefader ():
    """ Fader-Seite:
    sendet Daten zu cuefaders und exefaders
    Die Fadertabelle ist bereits bei load_fadertable erzeugt
    data: je ein dict für jede location von Fadern
    """
    data = get_faderdata ()
    
    if data["found_data"] == "false":
        flash ("Es sind noch keine Fader vorhanden.")
    return render_template ("cuefader.html", data = data )


@basic.route ("/fadertable")
@basic.route ("/fadertable/<sel>")
@login_required
@standarduser_required
def fadertable (sel:str=""):
    """ Fader-Seite einrichten/bearbeiten 
    eine der Fader-Tabellen wird angezeigt. Auswahl der angezeigten
    Tabelle wird in session gespeichert
    sel: cuefaders oder exefaders
    """
    # data = get_faderdata ()

    if sel:
        session["selected_fadertable"] = sel
    elif "selected_fadertable" in session:
        sel = session["selected_fadertable"]
    else:
        sel = "exefaders"
        session["selected_fadertable"] = sel

    locations = {} # Daten für File-Selector
    for loc in fader_locations:
        if loc == sel:
            status = "active"
        else:
            status = ""
        cfgdata = globs.cfg.get (loc)
        locations[loc] = { "text":cfgdata,  # data[loc]["shortname"],
                            "status":status,
                            "cuelist":loc}

    fname = globs.cfg.get(sel)
    filename = os.path.join (globs.room.cuefaderpath(),fname)
    csvfile = Csvfile (filename)
    if csvfile.changed():
        changes = "true"
    else:
        changes = "false"
    
    check_clipboard ()

    return render_template ("cuefader-setup.html", 
                    locations = locations,
                    shortname = csvfile.shortname(),
                    pluspath = csvfile.pluspath(),
                    fieldnames = csvfile.fieldnames(),
                    items = csvfile.to_dictlist(), 
                    changes = changes,
                    option  = "cuefader", #sel, # 'cuefaders' oder 'exefaders'
                    loc = sel,
                    filebuttons = "cue", # in macro csvtble-macros.html -> table
                    excludebuttons = [] )


@basic.route ("/cuebutton")
@login_required
def cuebutton ():
    """ Button-Seite 
    """
    data = get_buttondata ()
    
    if data["found_data"] == "false":
        flash ("Es sind noch keine Buttons vorhanden.")
    return render_template ("cuebutton.html", data = data )


@basic.route ("/buttontable")
@basic.route ("/buttontable/<sel>")
@login_required
@standarduser_required
def buttontable (sel:str=""):
    """ Button-Seite einrichten/bearbeiten
    sel: cuebuttons, exebuttons1, exebuttons2
    """
    # data = get_buttondata ()
    check_clipboard ()

    if sel:
        session["selected_buttontable"] = sel
    elif "selected_buttontable" in session:
        sel = session["selected_buttontable"]
    else:
        sel = "exebuttons1"
        session["selected_buttontable"] = sel

    locations = {}
    for loc in button_locations:
        if loc == sel:
            status = "active"
        else:
            status = ""
        cfgdata = globs.cfg.get (loc)
        locations[loc] = { "text":   cfgdata, #data[loc]["shortname"],
                           "status": status,
                           "cuelist":loc}

    # Daten von der csv-Datei holen:                            
    fname = globs.cfg.get(sel)
    filename = os.path.join (globs.room.cuebuttonpath(),fname)
    csvfile = Csvfile (filename)
    if csvfile.changed():
        changes = "true"
    else:
        changes = "false"

    return render_template ("cuebutton-setup.html", 
                    locations = locations,
                    shortname = csvfile.shortname(),
                    pluspath = csvfile.pluspath(),
                    fieldnames = csvfile.fieldnames(),
                    items = csvfile.to_dictlist(), 
                    changes = changes,
                    option  = "cuebutton", # sel
                    loc = sel,
                    filebuttons = "cue",
                    excludebuttons = [] )


@basic.route ("/exec")
@login_required
def exec ():
    """ Kombi-Seite mit Buttons und Fadern
    optional:  
        ein Button-Block
        ein Fader-Block
        ein Button-Block
    """
    # session["editmode"] = "select" # editmode select ohne message
    faderdata = get_faderdata ()
    buttondata = get_buttondata ()
    return render_template ("exec.html", 
                faderdata = faderdata,
                buttondata = buttondata )
    

@basic.route ("/doku")
@basic.route ("/doku/<page>")
def doku (page:str=None) :
    """ html-Seite aus Doku-Ordner 
    return: HTML
    """
    if page:
        docpage = "doku/" + page + ".html"
        session["docpage"] = page
    else:
        if "docpage" in session:
            docpage = "doku/" + session["docpage"] + ".html"
        else:
            docpage = "doku/impressum.html"
    return render_template (docpage)


@basic.route ("/galerie")   
def galerie ():
    """ Bildergalerie anzeigen
    """
    pictures = list_pictures()
    return render_template ("gallery.html", pictures = pictures)


@basic.route ("/viewlog")
@login_required
@standarduser_required
def viewlog ():
    """ Logfile anzeigen 
    """
    logdir = os.path.join (globs.basedir, "logs")
    logdir = logdir.replace (os.sep, '+')
    return render_template ("viewlog.html", logdir=logdir)


@basic.route ("/getlogfile")
def getlogfile () ->json:
    """ Logfile  in HTML 

    return im JSON-Format
    """
    # aktuell angezeigtes logfile in session speichern:
    fullname = request.args.get ("name")

    if fullname != "" and fullname != "undefined":
        session["logname"] = fullname
    else:
        if "logname" in session:
            fullname = session["logname"]
        else:
            return "kein Logfile ausgewählt."
    
    fullname = fullname.replace ('+', os.sep) # '+' in '/' umwandeln
    path, shortname = os.path.split (fullname)
    loglines = readlogfile (fullname)

    table = render_template ("logfile.html",
                    shortname = shortname, 
                    fullname = fullname,
                    lines = loglines)
    return json.dumps (table)
