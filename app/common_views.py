#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import sys

from flask import Blueprint, render_template, request, json, redirect
from flask import session, flash, url_for #, send_from_directory
from flask_login import login_required
# from cuebutton import Cuebutton

from apputils import standarduser_required, admin_required, redirect_url
from apputils import calc_mixoutput, press_cuebutton, midifader_monitor

import globs

from csvfileclass import Csvfile
from roomclass import Room
from startup import load_config
# from startup_func import fadertable_items
from filedialog_util import list_dir


common = Blueprint ("common", __name__, url_prefix="", 
                  static_folder="static", template_folder="templates")

# --- Bootstrap Theme --------------------------------------------
@common.route ("/bootstraptheme/<theme>")
def bootstraptheme (theme:str):
    """ Thema für Seiten-Layout
    in session gespeichert
    """
    themes = ["cyborg","darkly","flatly","spacelab","superhero"]
    if theme in themes:
        session["bootstraptheme"] = theme
        flash (f"Thema {theme} ausgewählt.")
    elif theme == "default":
        if "bootstraptheme" in session:
            session.pop ("bootstraptheme")
            flash ("Standard-Thema ausgewählt.")
    else:
        flash (f"Thema {theme} nicht vorhanden.", category="danger")
    return redirect (redirect_url())

# --- Edit/Select Umschaltung ------------------------------------
@common.route ("/editmode/<mode>")
@login_required
def editmode (mode:str=""):
    """ Bearbeitungsmodus: edit/select

    edit: Zellen bearbeiten
    select: Objektauswahl, z.B. Zeile in CSV oder Head in Stage
    """
    modes = ["edit","select"] #,"view"]
    modetext = ["EDIT", "SELECT"] #, "AUS"]
    if mode in modes:
        session["editmode"] = mode
        i = modes.index (mode)
        return modetext[i]
    else:
        return "SELECT"

# --- Clipboard ---------------------------------------------------
def check_clipboard ():
    """ session['csvclipboard'] auf  'true' setzen oder löschen
    """
    if Csvfile.clipboard:
        session["csvclipboard"] = "true"
    else:
        session.pop ("csvclipboard", None)


# --- Tests: --------------------------------------------------------
@common.route ("/testtable")
def testtable ():
    return render_template ("data/dataedit.html", spath="testtbl")

@common.route ("/test")
def test ():
    """ Test cuebutton-table 
    """
    room = Room () # default Room
    testpath = room.cuebuttonpath ()
    pluspath = testpath.replace (os.sep, '+')
    shortname = "testbuttons"
    fullname = os.path.join (testpath, shortname)
    csvfile = Csvfile (fullname)

    return render_template ("test_table.html", 
        shortname = shortname,
        pluspath = pluspath,
        fieldnames = csvfile.fieldnames (),
        items = csvfile.to_dictlist (),
        option = "cuebutton")


@common.route ("/testsvg")
def testsvg ():
    return render_template ("testsvg.html")


@common.route ("/contrib")
@login_required
@admin_required
def contrib ():
    """ contrib anzeigen """
    fieldnames = ["index", "key", "level", "extra"]
    items = globs.Cue.contrib.to_dictlist ()
    return render_template ("contrib.html", 
        fieldnames = fieldnames,
        style = "table-sm table-striped",
        items = items)


@common.route ("/reload")
@login_required
def reload ():
    """ config neu laden """
    load_config (with_savedlevels=True)
    return redirect (redirect_url())


# --- Info ---------------------------------------------------------

@common.route('/getinfo/<item>')
def get_info (item:str) -> json:
    """ Infos an Javascript übermitteln
    in JS: $.get ('/getinfo/<item>', function(data) {...
    liefert data zurück
    """
    if item == "sliderval":       # sliderwerte übermitteln für Seitenaufbau
        sliders = len (globs.fadertable)
        bytevals = [int (globs.fadertable[i].level *255) for i in range (sliders)]
        return json.dumps (bytevals)

    elif item == "buttonval":       # faderwerte übermitteln für Seitenaufbau
        # nicht in Verwendung?
        buttons = len (globs.buttontable)
        bytevals = [int (globs.buttontable[i].level *255) for i in range (buttons)]
        return json.dumps (bytevals)

    elif item == "buttonstatus":  # Buttonstatus übermittlen
        buttons = len (globs.buttontable)
        buttonstat = [globs.buttontable[i].status for i in range (buttons)]
        return json.dumps (buttonstat)
    
    elif item == "mix": # Mix output 
        unis = globs.cfg.get ("universes")
        items = []
        if globs.PYTHONANYWHERE == "true":
            # keine threads, daher aktuelle Berechnungen machen:
            calc_mixoutput ()
        for uni in range (1,int(unis)+1):
            mix = globs.patch.show_mix (uni)
            # print (f"mix-{uni}: {mix}")
            for i in range (len (mix)):
                if mix[i]:
                    items.append (f"{uni}-{i+1}:{mix[i]}")
        out = render_template ("output-content.html", items = items)
        return json.dumps (out)

    elif item == "firstattribute": 
        # Wert für erstes Attribut jedes Heads
        # das ist in der Regel Intensity
        # verwendet in stage.html für progressbars
        if globs.PYTHONANYWHERE == "true":
            # keine threads, daher aktuelle Berechnungen machen:
            calc_mixoutput ()
        attlevels = {}
        headlist = globs.patch.headlist ()
        for head in headlist:
            attlist = globs.patch.attriblist (head)
            level = int (globs.patch.attribute (head, attlist[0]))
            # der Default-Wert ist str
            attlevels[head] = f"{int (100*level/255)}%"
            # levels in %
        return json.dumps (attlevels)

    elif item == "layout":
        # Layout-Infos zu Feld 
        subdir = request.args.get ("subdir")
        field  = request.args.get ("field") # Kleinbuchstaben
        rule = globs.room.layout.rule (subdir + field)
        return json.dumps (rule)

    return json.dumps("???")


@common.route ("/getheads")
def getheads ():
    """ die Heads ald Liste liefern 
    """
    heads = globs.patch.headlist ()
    return json.dumps (heads)

@common.route ("/getattribs/<headnr>")
def getattribs (headnr:str):
    """ attribute zu Head 'headnr' liefern 
    """
    attribs = globs.patch.attriblist (headnr)
    return json.dumps (attribs)


@common.route ("/notinpythonanywhere")
def notinpythonanywhere ():
    """ Message: 'in Pythonanywhere nicht verfügbar'
    """
    flash ("Diese Funktion ist in Pythonanywhere nicht verfügbar")
    return redirect (redirect_url())


@common.route ("/output")
def output ():
    """ Mix-Output anzeigen
    """
    return render_template ("output.html")


# --- Cue-Slider -------------------------------------------------------
@common.route("/sliderlevel/<int:index>", methods = ["POST"])
def sliderlevel(index:int) -> str:
    """ Sliderlevel von Javascript empfangen
    index ab 0
    """
    level = 0
    # index = slider-1
    sliders = len (globs.fadertable)
    if index in range (sliders):
        level = request.form["level"]
        globs.fadertable[index].level = float(level) / 255
        # midifader_monitor (1+index, int (level)/2)
    return "ok"


# --- Cuelist Level Slider -----------------------------------------------
@common.route("/cuelistlevel/<int:index>", methods = ["POST"])
def cuelistlevel(index:int) -> str:
    """ Sliderlevel von Javascript empfangen
    index ab 0
    """
    level = 0
    # index = slider-1
    sliders = len (globs.cltable)
    if index in range (sliders):
        level = request.form["level"]
        globs.cltable[index].level = float(level) / 255
        if globs.PYTHONANYWHERE == "false" and globs.midiactive:
            pass
            # globs.MidiOutput.level ()
    return "ok"


# --- Button -------------------------------------------------------------
@common.route("/buttonpress")
def buttonpress () -> str:
    """ Cuebutton drücken """
    butt = request.args.get ("index") 
    index = int(butt)
    press_cuebutton (index)
    return "ok"


# --- View ICONS in /static/icons -----------------------------------
@common.route ("/viewicons")
@login_required
@admin_required
def viewicons ():
    """ zeige alle Icons und die dazu gehörigen Dateinamen
    """
    # https://stackoverflow.com/questions/1475123/easiest-way-to-turn-a-list-into-an-html-table-in-python
    def row_major(alist, sublen):      
        return [alist[i:i+sublen] for i in range(0, len(alist), sublen)]

    icondir = os.path.join (common.static_folder, "icons")
    content = list_dir (icondir, ".svg")
    items = content["file"]
    # items = []
    # for item in files:
    #     root, ext = os.path.splitext(item)
    #     items.append (root)

    # items in Reihen zu 4 Elementen:
    itemtable = []    
    for r in row_major (items, 4):
        itemtable.append (r)

    return render_template ("viewicons.html", itemtable=itemtable)

    
