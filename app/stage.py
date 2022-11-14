#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import csv
from copy import deepcopy

from flask import Blueprint, render_template, request, json
from flask import url_for, flash, redirect, session, make_response
from flask_login import login_required, current_user

from apputils import standarduser_required, redirect_url
from apputils import calc_mixoutput

from csvfileclass import Csvfile
from csvnameclass import Csvname
from sort import natural_keys
# from common_views import editmode 

import globs


stage = Blueprint ("stage", __name__, url_prefix="/stage",
                   static_folder="static", template_folder="templates")

# hier werden die Singlehead-Indizes der User gesammelt:
singleindexdict = {}

def get_stage_filename () -> str:
    """ Filename der Stage 

    entweder session["stagename"] oder globs.cfg.get("stage")
    testen, ob File existiert
    """
    fname = globs.cfg.get("stage")    
    if "stagename" in session:
        stagename = os.path.join (globs.room.stagepath(), session["stagename"])
        checkname = Csvname (stagename)
        if checkname.exists ():
            return stagename

    fname = globs.cfg.get("stage")
    if not fname: # sollte nicht vorkommen, siehe startup
        fname = "_neu"
    stagename = os.path.join (globs.room.stagepath(),fname)
    checkname = Csvname (stagename)
    if checkname.exists ():
        return stagename
    else:
        return os.path.join (globs.room.stagepath(),"_neu")


def px_to_int (s:str) ->int:
    """ 'px' von String Ende abschneiden
    """
    if s.endswith ("px"):
        return int (round (float (s[:-2])))
    else:
        return int (round (float (s)))


def int_to_pix (i:str) ->str:
    """ px an i anhängen, Komma abtrennen """
    s = i.split (sep=".")    
    if not s[0].endswith ("px"): 
        return s[0] + "px"
    return s[0]


def check_px (items:list):
    """ Left, Top, Width und Height anpassen
    'px' anhängen
    """
    for item in items:
        if "Left" in item:
            num = item["Left"]
            item["Left"] = int_to_pix (num)
        if "Top" in item:
            num = item["Top"]
            item["Top"] = int_to_pix (num)
        if "Width" in item:
            num = item["Width"]
            item["Width"] = int_to_pix (num)
        if "Height" in item:
            num = item["Height"]
            item["Height"] = int_to_pix (num)
        
# --- Stage-Seiten ------------------------------------------------

@stage.route("/show")
@stage.route("/show/<mode>")
@login_required
def show(mode=""):
    """ Stage erzeugen

    - von Config: 'stage.csv'
    - von stage.csv die Elemente in items einlesen
    - an stage.html übergeben und dort Seite rendern
    mode 'mobil' liefert Stage-Mobil, sonst Standard-Stage
    """

    # selektierte Heads leeren
    if "headstring" in session:
        session.pop ("headstring", None)

    fullname = get_stage_filename ()
    csvfile = Csvfile (fullname)
    if csvfile.changed():
        changes = "true"
    else:
        changes = "false"

    if mode == "mobil":
        sortlist = sorted (csvfile.to_dictlist (), 
            key = lambda x: natural_keys (x["Name"]))

        return render_template ("stage_mobil.html", 
            shortname = csvfile.shortname(), 
            fieldnames = csvfile.fieldnames (), 
            items     = sortlist,
            file      = csvfile.longname(),
            pluspath  = csvfile.pluspath(),
            changes   = changes,
            option    = "stage",
            excludebuttons=[])

    items = csvfile.to_dictlist ()
    check_px (items)

    # Sichtbarkeit der Felder:
    itemview = {}
    for field in ["Name", "Text", "Comment"] :
        if "itemview"+field in session:
            itemview[field] = session["itemview"+field]
        else:
            itemview[field] = "checked"

    return render_template ("stage.html", shortname = csvfile.shortname(), 
                             fieldnames = csvfile.fieldnames (), 
                             items     = items,
                             file      = csvfile.longname(),
                             pluspath  = csvfile.pluspath(),
                             changes   = changes,
                             option    = "stage",
                             itemview  = itemview,
                             excludebuttons=[])


@stage.route ("/update_item")
@standarduser_required
def update_item ():
    """ Stage-Item in csv-Tabelle updaten
    """
    fullname = get_stage_filename ()
    csvfile = Csvfile (fullname)
    # row_num = request.args.get ("row_num")
    jdata = request.args.get ("data")
    data = json.loads (jdata)
    for key, value in data.items():
        csvfile.update_line (value)
    return "ok"


@stage.route ("/itemviewmode")
def itemviewmode () :
    """ Sichtbarkeit der Textstrings steuern
    
    Die Sichtbarkeit der Felder Name, Text und Comment kann ein oder aus
    sein. Default == ein.
    """
    field = request.args.get ("field")
    value = request.args.get ("value")

    if field in ["Name", "Text", "Comment"] :
        if value == "false":
            session["itemview"+field] = ""
        else:
            session["itemview"+field] = "checked"
    return "ok"
    

@stage.route ("/headmodal", methods=['GET','POST'])
def headmodal ():
    """ Modal für eine Auswahl an Heads erzeugen 

    GET:  Modal erzeugen 
    POST: nichts zu tun, die Arbeit erledigt headfader()
    """
    if request.method == 'POST':
        return "ok"

    return render_template ("modaldialog.html", body="faderbody",
                            title="Selektion: ")


@stage.route ("/headfader", methods=['GET','POST'])
def headfader ():
    """ Fader für eine Auswahl an Heads erzeugen / mixen

    GET:  Fader erzeugen
    POST: Faderdaten an Mix schicken 
    """
    if request.method == 'POST':
        hd     = request.form["head"]
        attrib = request.form["attrib"]
        level  = request.form["level"]
        heads  = hd.split ('-') # am Ende steht leider ''
        for head in heads:
            if len (head):
                globs.topcue.add_item (head, attrib, level)
        return "ok"
    
    headlist = globs.patch.headlist ()
    hd = request.args.get ("heads")
    if not hd:
        hd = headlist[0]
        singleindex = "0"
    else:
        singleindex = request.args.get ("single")
    if singleindex:
        session ["singleheadindex"] = singleindex
        singleindexdict[current_user.username] = singleindex
        # print ("headindex:", singleindex)
    requestheads = hd.split ()
    # Duplikate entfernen:
    # siehe https://www.w3schools.com/python/python_howto_remove_duplicates.asp
    requestheads = list (dict.fromkeys(requestheads))
    requestheads = sorted (requestheads, key=natural_keys)
    headstring = ""
    for item in requestheads:
        headstring = headstring + item + ' '
    session["headstring"] = headstring

    ret = {}
    # Attribute und Levels pro Head abfragen
    # jedes Attribut in retattribs nur 1x eintragen
    # level: maximum aus den Einzelnen Heads
    retheads   = {} 
    # retheads Struktur: {"att-1":"1-2-5-", "att-2":"1-3-7-",}
    # für table: in Liste konvertieren = retheadlist

    retattribs = []
    retlevels  = {} # für die for-loop als int abspeichern
    if globs.PYTHONANYWHERE == "true":
        calc_mixoutput ()
    for head in requestheads:
        if head in headlist:
            heads  = [] # wird für attribslider.html benötigt, hier: [head,head,...]
            attribs = globs.patch.attriblist (head)
            for att in attribs:
                level = int (globs.patch.attribute (head, att))
                if att in retattribs:
                    retheads[att] = retheads[att] + head + '-'
                    retlevels[att] = max (retlevels[att], level)
                else:
                    retattribs.append (att)
                    retheads[att] = head + '-'
                    retlevels[att] = level

    # retheadlist erzeugen, retlevels in str konvertieren:
    retheadlist = []
    for att in retattribs:
        retheadlist.append (retheads[att])
    # for key in retlevels.keys():
    #     retlevels[key] = str (retlevels[key])
    if not len (retheadlist): # keine heads gefunden
        ret["errortext"] = f"Die gewählten Elemente sind nicht im Patch!"

    ret["attribs"] = retattribs
    ret["levels"]  = retlevels
    ret["heads"]   = retheadlist
    ret["headstring"] = headstring
    ret["table"]   = render_template ("attribslider.html", 
                                    heads=retheadlist,
                                    attribs=retattribs,
                                    labels=retattribs,
                                    title=hd)
    return json.dumps (ret)


@stage.route ("/headdetails")
def headdetails ():
    """ Detail-Tabelle zu Head erzeugen
    """
    hd = request.args.get ("heads")
    # requestheads = hd.split ()
    fieldnames = globs.patch.pfields().copy()
    if "HeadNr" in fieldnames:
        fieldnames.remove ("HeadNr")
    ret = {}
    ret ["details"] = render_template ("csvtable.html",
                        shortname = "undefined",
                        fieldnames = fieldnames,
                        items = globs.patch.headdetails (hd))
    return json.dumps (ret)





# @stage.route ("/oneheadfader", methods=['GET','POST'])
# def oneheadfader ():
#     """ Fader für einen Head erzeugen 

#     Faderdaten an Mix schicken """

#     if request.method == 'POST':
#         head   = request.form["head"]
#         attrib = request.form["attrib"]
#         level  = request.form["level"]
#         globs.topcue.add_item (head, attrib, level)
#         return "ok"
#         # print (f"Head: {head}, Attribut: {attrib}, Level: {level}")
    
#     head = request.args.get ("head")
#     headlist = globs.patch.headlist ()
#     if head in headlist:
#         ret = {}
#         attribs = globs.patch.attriblist (head)
#         ret["attribs"] = attribs
#         levels = {}
#         heads  = [] # wird für attribslider.html benötigt, hier: [head,head,...]
#         for att in attribs:
#             levels[att] = globs.patch.attribute (head, att)
#             heads.append (head)
#         ret["levels"] = levels
#         ret["table"]   = render_template ("attribslider.html", 
#                                          heads=heads,
#                                          attribs=attribs,
#                                          labels=attribs,
#                                          title="Head: "+head)
#         return json.dumps (ret)
#     else:
#         return "false"


@stage.route ("/import_patch")
def import_patch ():
    """ für alle Heads aus Patch ein Element auf der Stage erzeugen 

    Unterhalb von vorhandenen Items Reihen von je 6 Elementen
    """
    stagename  = get_stage_filename ()
    stagefile = Csvfile (stagename)
    # headlist = globs.patch.headlist ()

    # Einfügepunkt unterhalb von vorhandenen Elementen:
    items = stagefile.to_dictlist ()
    if len (items):
        tops = []
        heights = []
        for item in items:
            # 'px' abschneiden und in int wandeln:
            tops.append (px_to_int ( item["Top"]))
            heights.append (px_to_int (item["Height"]))
        maxtop = max (tops)
        maxheight = max (heights)
    else:
        maxtop = 0
        maxheight = 0

    # Liste der bereits vorhandenen Heads:
    stageheads = []
    for item in items:
        if item["Type"] == "Head":
            stageheads.append (item["Name"])

    # liste der neuen Head-Elemente erzeugen:
    distx = 90 # x-Abstand
    disty = 160 # y-Abstand
    max_in_row = 6 # maximale Elemente pro Reihe
    inserttop = 20 + maxtop + maxheight
    newheads = []
    count = 0
    elem = {}
    # for head in headlist:
    for key in globs.patch.pdict.keys ():
        patchline = globs.patch.patch_line (key)
        if patchline["HeadNr"] not in stageheads: # nur neue Elemente
            if count >= max_in_row:
                count = 0
                inserttop = inserttop + disty
            elem.clear ()
            elem["Name"] =   patchline["HeadNr"]
            elem["Type"] =   "Head"
            elem["Text"] =   patchline["Name"]
            elem["Comment"]= patchline["Comment"] 
            elem["Left"] =   str (20 + count * distx) 
            elem["Top"]  =   str (20 + inserttop) 
            elem["Width"] =  str (distx - 20) 
            elem["Height"] = str (disty - 20) 
            
            newheads.append (deepcopy (elem))
            count = count+1

    stagefile.add_lines (newheads)

    return redirect (redirect_url())


@stage.route ("/single")
@login_required
def single ():
    """ Head-Einzelsteuerung
    """
    # print ("session-singleheadindex:", singleindex () )
    return render_template ("single.html", 
                    headindex = singleindex (),
                    headlist = globs.patch.headlist (),
                    excludebuttons=[])


@stage.route ("/singleindex")
@login_required
def singleindex ():
    """ Head-Einzelsteuerung

    den zuletzt angezeigten Head liefern
    """
    if current_user.username in singleindexdict.keys():
        return singleindexdict[current_user.username]
    elif "singleheadindex" in session:
        return str (session["singleheadindex"])
    else:
        return "0"



# -------------------------------------------------------------------------
# Modul-Test:    
if __name__ == "__main__":
    fname = "conftest.csv"
    csvfile = Csvfile (fname)

    print ("Fieldnames: ", csvfile.fieldnames())
    data = csvfile.to_dictlist()
    print ("data: ", data)
    print ("data[0]: ", data[0])
    print ("data[1]['value']: ", data[1]['value'])