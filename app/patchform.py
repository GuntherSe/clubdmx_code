#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" View zur Erzeugung von Patch-Einträgen """

import os
import os.path
import math

from flask import Blueprint, render_template, request, redirect 
from flask import url_for, flash, session
from wtforms import Form, StringField, IntegerField, SelectField
from wtforms import validators
from flask_login import login_required, current_user

import globs

from csvfileclass import Csvfile
from apputils import redirect_url
from apputils import standarduser_required #, admin_required, redirect_url 
# from startup import load_config
from csv_views import evaluate_option
from formutils import onoff_choices, dir_choices, leave_form

patchform = Blueprint ("patchform", __name__, url_prefix="/", 
                     static_folder="static", template_folder="templates")

current_headtype = ""

def dmxlength (headtype:str) ->int:
    """ Anzahl der dmx-Werte von Head 'headtype'
    """
    headpath = globs.patch.HEADPATH
    csvfile = Csvfile (os.path.join (headpath, headtype))
    fieldnames = csvfile.fieldnames ()
    data = csvfile.to_dictlist ()
    offsets = []
    for d in data:
        if "Size" in fieldnames:
            size = math.ceil (int (d["Size"]) / 8) # 1 oder 2
        else:
            size = 1

        try:
            offsets.append (int (d["Addr"]) + size)
        except: # Head mit Virtual Dimmer, Addr == 'v'
            pass
        
    return max (offsets)


def new_patch_lines (data:dict) ->list:
    """ Form-Daten für Csvfile.add_lines aufbereiten 
    """
    lines = []
    headcount = data["headcount"]
    headtype = data["headtype"]
    headlength = dmxlength (headtype)
    headnr = data["headnr"] #int
    address = data["address"] # uni-addr
    name = data["name"]
    if headcount > 1:
        namestring = name + " 1"
    else:
        namestring = name

    # address prüfen:
    uni, chan = address.split (sep='-')
    cnt = int(chan) + headlength
    if cnt + headlength > 511:
        return []

    for i in range (headcount):
        line = {"HeadType":headtype, 
                "Gel":data["gel"],
                "Comment":data["comment"]}
        line["HeadNr"] = str(headnr)
        line["Addr"] = address
        line["Name"] = namestring
        lines.append (line)
        # nächste Zeile vorbereiten
        uni, chan = address.split (sep='-')
        cnt = int(chan) + headlength
        if cnt + headlength < 512:
            address = f"{uni}-{cnt}"
            headnr = headnr + 1
            namestring = f"{name} {str(i+2)}"
        else:
            break
    return lines


@patchform.route ("/patchnew", methods=['GET', 'POST'])
@login_required
@standarduser_required
def patchnew ():
    """ Form zur Erzeugung von Patch-Einträgen
    """
    global current_headtype
    fullname = globs.patch.file.name ()
    csvfile = Csvfile (fullname)
    headdir_choices = dir_choices ("head")
    headlist = globs.patch.headlist() # ist sortiert
    try:
        lasthead = int (headlist[-1])
        nexthead = 1 + lasthead
    except: # leerer Patch
        nexthead = 1
    addressrule = globs.room.layout.rule ("patchaddr")
    description = {"placeholder":addressrule["placeholder"]}

    class Patchform (Form):
        headcount    = IntegerField ("Anzahl neuer Heads", default=1,
                validators=[validators.InputRequired(message="Pflichtfeld!")])
        headnr       = IntegerField ("Head-Nummer", default=nexthead,
                validators=[validators.InputRequired(message="Pflichtfeld!")])
        headtype     = SelectField ("Head-Typ", choices=headdir_choices,
                default=current_headtype,
                validators=[validators.InputRequired(message="Pflichtfeld!")])
        address      = StringField ("Adresse", description=description,
                validators=[validators.InputRequired(message="Pflichtfeld!")])
        name         = StringField ("Name")
        gel          = StringField ("Farbe")
        comment      = StringField ("Kommentar")

    form = Patchform (request.form)

    if request.method == 'POST':
        if request.form["submit_button"] != "true": # schließen-Button
            return leave_form ()

        elif    form.validate ():                   # Daten ok
            # print ("Data: ", form.data)
            lines = new_patch_lines (form.data)
            ret = csvfile.add_lines (lines)
            if ret["tablechanged"] == "true":
                evaluate_option ("patch")
            flash (ret["message"], category=ret["category"])
            return leave_form ()
        
        else:                                       # falsche Daten
            session["retry_the_form"] = "true"

    if "retry_the_form" not in session:
        session["nexturl"] = request.referrer
    return render_template("patchform.html", form = form,
                            shortname = globs.patch.file.shortname())
    


