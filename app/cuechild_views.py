#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Cuechild-Views :

- Topcue-Views
"""

from glob import glob
import os
import os.path

from flask  import Blueprint, request, json, flash
from flask  import redirect, url_for, render_template, session

from csvfileclass import Csvfile
from cue import Cue
from startup_func import make_fadertable, make_cuebuttons
from apputils import standarduser_required, admin_required, redirect_url
from csv_views import evaluate_option


import globs

cuechild = Blueprint ("cuechild", __name__, url_prefix="/cuechild",
                    static_folder="static", template_folder="templates")


@cuechild.route ("/cuemodal", methods = ["GET","POST"])
def cuemodal ():
    """ Cue in Modal anzeigen """

    if request.method == 'POST':
        return "ok"

    return render_template ("modaldialog.html", body="faderbody",
                                                title="Cue-Daten",
                                                submit_text="speichern")


@cuechild.route ("/topclear")
def topclear ():
    """ topcue-Einträge löschen """

    locationreload = request.args.get ("reload")
    # Cue.contrib.pause ()
    globs.topcue.clear ()
    # session.pop ("topcuecontent", None)
    # Cue.contrib.resume ()
    if locationreload == "false":
        return "ok"
    else:
        return redirect (redirect_url())


@cuechild.route ("/topview", methods = ["GET","POST"])
def topview ():
    """ topcue in Modal anzeigen """

    if request.method == 'POST':
        return "ok"

    fieldnames = globs.topcue._cuefields
    items      = globs.topcue.to_dictlist ()
    excludebuttons = ["openButton", "saveasButton", "newlineButton",
                      "uploadButton", "saveChanges", "discardChanges",
                      "selectRowCut", "selectCopy", "selectPaste",
                      "clearClipboard"]

    return render_template ("modaldialog.html", body="csvbody",
                                                title="Topcue-Daten",
                                                shortname="Topcue Inhalt",
                                                pluspath="",
                                                fieldnames=fieldnames,
                                                items=items,
                                                excludebuttons=excludebuttons,
                                                option="cue")


# --- Topcue sichern --------------------------------------------------------

@cuechild.route ("/topsave/<option>", methods = ["GET","POST"])  
@standarduser_required
def topsave (option:str):
    """ topcue als Cue, Fader oder Button speichern.
    
    als Cue speichern: filedialog Modal aufrufen und Cuefile wählen
      kann auch existierendes File sein, dann update
    als Fader oder Button speichern: string Modal aufrufen und Bezeichnung wählen
      dann Cuenamen generieren und topcue speichern
      anschließend Fader bzw. Button erzeugen 
    """
    if request.method == 'POST':
        cuepath = globs.room.cuepath ()

        if option == "fader":
            filename = request.form["name"]
        elif option == "button":
            filename = request.form["name"]
        elif option == "cuelist":
            filename = request.form["name"]
        else: # option == 'cue'
            filename = request.form["filename"]

        if len (filename): # Filename eingegeben:
            # neuen Cue anlegen 
            filename = filename.replace ('+', '_') # '+' nicht im Namen!
            fullname = os.path.join (cuepath, filename)
            csvfile = Csvfile (fullname)
            if os.path.isfile (csvfile.name()):
                ret = globs.topcue.merge_to_csv (csvfile)
            else:
                ret = globs.topcue.to_csv (csvfile)
                # automatisches update von Cue
                # evaluate_option ("cue")
            flash (ret["message"], category=ret["category"])

            # Option auswerten:
            if option == "fader":
                faderpath = globs.room.cuefaderpath ()
                faderfile = globs.cfg.get ("exefaders")
                fullname = os.path.join (faderpath, faderfile)
                csvfile.name (fullname)

                if faderfile == "_neu": # default-Name festlegen
                    globs.cfg.set ("exefaders", "exefader")
                    globs.cfg.save_data ()
                    faderfile = "exefader"
                    # File anlegen:
                    dst = os.path.join (faderpath, "exefader")
                    csvfile.backup (dst)
                    csvfile.name (dst)

                newline = {} 
                # defaults in newline eintragen:
                globs.room.check_csv_line (newline, "cuefader")
                newline["Filename"] = filename
                newline["Text"] = filename
                csvfile.add_lines ([newline])
                make_fadertable (with_savedlevels=True)
                flash (f"neuen Fader {filename} angelegt.", category="success")

            elif option == "button":
                buttonpath = globs.room.cuebuttonpath ()
                buttonfile = globs.cfg.get ("exebuttons1")
                fullname = os.path.join (buttonpath, buttonfile)
                csvfile.name (fullname)

                if buttonfile == "_neu": # default-Name festlegen
                    globs.cfg.set ("exebuttons1", "exebuttons")
                    globs.cfg.save_data ()
                    buttonfile = "exebuttons"
                    # File anlegen:
                    dst = os.path.join (buttonpath, "exebuttons")
                    csvfile.backup (dst)
                    csvfile.name (dst)

                newline = {}
                # defaults in newline eintragen:
                globs.room.check_csv_line (newline, "cuebutton")
                newline["Filename"] = filename
                newline["Text"] = filename
                csvfile.add_lines ([newline])
                make_cuebuttons (with_savedlevels=True)
                flash (f"neuen Button {filename} angelegt.", category="success")

            elif option == "cuelist":
                if "selected_cuelist" in session:
                    clpath = globs.room.cuelistpath ()
                    clfile = session["selected_cuelist"]
                    fullname = os.path.join (clpath, clfile)
                    csvfile.name (fullname)
                    newline = {}
                    # defaults in newline eintragen:
                    globs.room.check_csv_line (newline, "cuelist")
                    newline["Filename"] = filename
                    # Id ist vom Typ Counter:
                    nextid = csvfile.nextint ("Id")
                    newline["Id"] = nextid
                    csvfile.add_lines ([newline])
                    flash (f"Cueliste '{clfile}' um Zeile {nextid} erweitert.")
                else:
                    flash ("Keine Cueliste in Arbeit, Cue abgespeichert.")

        else:
            flash ("Kein Dateiname angegeben.", category="info")

        return "ok"

    ret = {}
    if option == "fader":
        return render_template ("modaldialog.html", title="Neuen Fader erzeugen",
                                                text="Fader-Bezeichnung:",
                                                body="stringbody",
                                                submit_text="erzeugen")

    elif option == "button":
        return render_template ("modaldialog.html", title="Neuen Button erzeugen",
                                                text="Button-Bezeichnung:",
                                                body="stringbody",
                                                submit_text="erzeugen")
    elif option == "cuelist":
        if "selected_cuelist" in session:
            title = "an Cuelist '" + session['selected_cuelist'] + "' anhängen"
        else:
            title = "keine Cueliste in Arbeit"
        return render_template ("modaldialog.html", title=title,
                                                text="Cue-Name:",
                                                body="stringbody",
                                                submit_text="erzeugen")
    else:
        ret["spath"] = "cue"  # request.args.get ("option")
        ret["ftype"] = ".csv"
        ret["dialogbox"] = render_template ("modaldialog.html", body = "filedialog",
                                title = "Topcue sichern")
        return json.dumps (ret)


@cuechild.route ("/update_cue")
def update_cue () ->dict:
    """ topcue in Cue integrieren, 
    alle Cues mit 'filename' in Fadertabelle und Buttontabelle updaten
    in allen Cuelisten currentcue und outcue updaten
    return: Message
    """
    filename = request.args.get ("filename")
    filename, ext = os.path.splitext (filename)
    fullname = os.path.join (globs.room.cuepath (), filename)
    csvfile = Csvfile (fullname)

    ret = globs.topcue.merge_to_csv (csvfile)

    for item in globs.fadertable:
        if item.file.shortname() == filename:
            globs.topcue.merge_to_cue (item)
    for item in globs.buttontable:
        if item.file.shortname() == filename:
            globs.topcue.merge_to_cue (item)
    for item in globs.cltable:
        if item.currentcue.file.shortname() == filename:
            globs.topcue.merge_to_cue (item.currentcue)
            globs.topcue.merge_to_cue (item.outcue)

    flash (ret["message"], category=ret["category"])
    return "ok"


# @cuechild.route ("/update_cuefader")
# def update_cuefader () ->dict:
#     """ topcue in cuefader[row_num-1] integrieren 
#     return: Message
#     """
#     row_num = request.args.get ("row_num")
#     cuenr = int (row_num) -1
#     option = request.args.get ("option")

#     if option == "cuefader":
#         sliders = len (globs.fadertable)
#         cuetable = globs.fadertable
#     else: # option == "cuebutton"
#         sliders = len (globs.buttontable)
#         cuetable = globs.buttontable

#     if cuenr in range (sliders):
#         fname = cuetable[cuenr].file.name()
#         csvfile = Csvfile (fname)

#         globs.topcue.merge_to_cue (cuetable[cuenr])
#         ret = globs.topcue.merge_to_csv (csvfile)

#         flash (ret["message"], category=ret["category"])
#     else:
#         flash ("Zeilennummer nicht gefunden", category="danger")
#     return "ok"
