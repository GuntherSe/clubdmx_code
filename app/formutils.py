#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Utilities für Forms: choices
"""

import os
import os.path

# from flask import Blueprint, render_template, request, json, redirect 
from flask import url_for, flash, session, redirect
# from wtforms import Form, StringField, IntegerField, SelectField, DecimalField
# # from wtforms import BooleanField
# from wtforms import validators
# from flask_login import login_required, current_user

import globs

from filedialog_util import list_dir
# from csvfileclass import Csvfile
# from mount import get_usbchoices
# from apputils import dbbackup, dbrestore
# from csv_views import evaluate_option
from apputils import redirect_url
# from startup import load_config



onoff_choices = [("0","aus"), ("1","ein")]

def dir_choices (subdir:str=None) ->list:
    """ choices-Liste aus roompath/subdir-Dateien
    
    return: Liste mit (filename,filename)-Tupel 
    ohne Extension am Filenamen
    """
    if subdir:
        roomdir = globs.room.path()
        searchdir = os.path.join (roomdir, subdir)
        ret = []
        content = list_dir (searchdir, ".csv")
        for elem in content["file"]:
            choice = os.path.splitext (elem)[0]
            ret.append ((choice, choice))
        return ret
    return [("nofile","keine Datei")]


def head_choices () ->list:
    """ choices-Liste aus verwendeten Headnummern """

    ret = []
    heads = globs.patch.headlist () # ist bereits sortiert
    # heads = sorted (heads)
    for head in heads:
        ret.append ((head,head))
    return ret


def leave_form ():
    """ Form verlassen und zu voriger Seite wechseln
    """
    session.pop ("retry_the_form", None)
    if "nexturl" in session and session["nexturl"]:
        nexturl = session.pop ("nexturl")
        return redirect (nexturl)
    return  redirect (redirect_url())


