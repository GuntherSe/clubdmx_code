#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Views zu class Csvfile Teil 2:
Zeilen-Operationen: ausschneiden, einfügen, ...
"""

import os
import os.path
import csv

from flask import Blueprint, render_template, request, json, redirect 
from flask import url_for, flash, session
from flask_login import current_user

import globs

from csvfileclass import Csvfile
from apputils import redirect_url
from csv_views import evaluate_option 
from stage import px_to_int

csvcutpaste = Blueprint ("csvcutpaste", __name__, url_prefix="/csv", 
                     static_folder="static", template_folder="templates")

# hier werden die selektierten Reihen gesammelt:
# Anm: mit Session-Cookies hauts nicht hin
selectedrowdict = {}

def clipboarddata () ->list:
    """ die selektierten Reihen des Users liefern
    """
    if current_user.username in selectedrowdict.keys():
        return selectedrowdict[current_user.username]
    else:
        return []

# --- Selektion von Zeilen: --------------------------------------------------- 

@csvcutpaste.route ("/selected_rows", methods=['POST'])
def selected_rows ():
    """ selektierte row-num's von JS empfangen

    geschickt von postSelectedRows 
    """
    rows   = request.form["rows"]
    rowlist = rows.split ()
    # session["selected_rows"] = rowlist
    selectedrowdict[current_user.username] = rowlist
    # print (f"Rows: {rowlist}")
    return "ok"


@csvcutpaste.route ("/remove_rows")
def remove_rows ():
    """ selektierte CSV-Zeilen löschen

    Selektion ist in session['selected_rows'] gespeichert
    """
    fname = request.args.get ("name")
    fname = fname.replace ('+', os.sep)
    option = request.args.get ("option")
    csvfile = Csvfile (fname)
    # Backup:
    csvfile.backup ()

    # zu löschende Zeilen:
    rowlist = clipboarddata ()
    # try:
    #     rowlist = session["selected_rows"] # str
    # except:
    #     rowlist = ""
    if len (rowlist):
        lines = [] # int
        for item in rowlist:
            line = int (item) -1
            lines.append (line)
        ret = csvfile.remove_lines (lines)
        evaluate_option (option)

        if ret["tablechanged"] == "true":
            session["csvclipboard"] = "true"
            flash (ret["message"], category="success")
    else:
        flash ("Zeilen nicht gelöscht.", category="danger")

    return redirect (redirect_url())


@csvcutpaste.route ("/copy_to_clipboard")
def copy_to_clipboard ():
    """ selektierte Zeilen in Clipboard kopieren 
    """
    fname = request.args.get ("name")
    fname = fname.replace ('+', os.sep)
    # option = request.args.get ("option")
    csvfile = Csvfile (fname)

    # zu kopierende Zeilen:
    # rowlist = session["selected_rows"] # str
    rowlist = clipboarddata ()
    if len (rowlist):
        lines = [] # int
        for item in rowlist:
            line = int (item) -1
            lines.append (line)
        ret = csvfile.copy_to_clipboard (lines)
        session["csvclipboard"] = "true"
        flash (ret["message"], category="success")
    else:
        flash ("Keine Auswahl an Zeilen.", category="info")

    return redirect (redirect_url())


def modify_clipboard (option:str):
    """ CSV Clipboard vor Paste anpassen
    zur Unterscheidbarkeit der Original-Zeilen
    TODO: hier alle Zeilen auf Defaultwerte testen, ggf hinzufügen.
    """
    # csvfile = Csvfile ("temp")
    if option == "stage":
        for item in Csvfile.clipboard:
            left = px_to_int(item["Left"])
            top  = px_to_int(item["Top"])
            item["Left"] = str (left + 30) #+ "px"
            item["Top"] =  str (top + 30) #+ "px"
            item["Text"] = item["Text"] + "(Kopie)"

    # für alle 'option': Defaults ergänzen
    for item in Csvfile.clipboard:
        globs.room.check_csv_line (item, option)
        

@csvcutpaste.route ("/paste_clipboard")
def paste_clipboard ():
    """ Csvfile.clipboard in Tabelle einfügen 
    """
    fname = request.args.get ("name")
    fname = fname.replace ('+', os.sep)
    option = request.args.get ("option")
    csvfile = Csvfile (fname)
    # Backup:
    csvfile.backup ()
    rowlist = clipboarddata ()
    # rowlist = session["selected_rows"]
    if len (rowlist):
        pos = int (rowlist[0])  # vor der ersten selektierten Zeile einfügen
    else:
        pos = 0 # append

    modify_clipboard (option)
    ret = csvfile.add_clipboard (pos)
    evaluate_option (option)

    if ret["tablechanged"] == "true":
        flash (ret["message"], category="success")
    else:
        flash ("Clipboard leer?", category="info")

    return redirect (redirect_url())


@csvcutpaste.route ("/clear_clipboard")
def clear_clipboard ():
    """ Csvfile.clipboard leeren
    """
    Csvfile.clipboard.clear ()
    session.pop ("csvclipboard", None)
    flash ("Clipboard geleert.", category="info")
    return redirect (redirect_url())

