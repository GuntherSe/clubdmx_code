#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Views zu class Csvfile """

import os
import os.path

from flask import Blueprint, render_template, request, redirect 
from flask import url_for, flash, session # , make_response
from wtforms import Form, StringField, IntegerField, SelectField, DecimalField
from wtforms import validators
from flask_login import login_required, current_user

import globs

from csvfileclass import Csvfile
from mount import get_usbchoices
from apputils import dbbackup, dbrestore
from csv_views import evaluate_option
from apputils import redirect_url
# from filedialog_util import list_dir
# from startup import load_config
from formutils import onoff_choices, dir_choices, head_choices, leave_form
from midiutils import command_choices

forms = Blueprint ("forms", __name__, url_prefix="/forms", 
                     static_folder="static", template_folder="templates")


def create_field (F:Form, field:str, rule:dict):
    """ dynamische Feld-Erzeugung
    siehe: http://wtforms.simplecodes.com/docs/1.0.1/specific_problems.html
    und https://wtforms.readthedocs.io/en/2.3.x/specific_problems/
    Ergebnis: Eintrag in F
    """
    if rule == {}:
        setattr (F, field, StringField (field))
    else:    
        # print (f"Regeln für {field}: {rule}")
        description = {}
        if "label" in rule:
            description["label"] = rule["label"]
        else:
            label = None

        if "default" in rule and len (rule["default"].strip()):
            default = rule["default"]
        else:
            default = None

        if "placeholder" in rule:
            description["placeholder"] = rule["placeholder"]

        if "required" in rule:
            validat = [validators.InputRequired(message="Pflichtfeld!")]
        else:
            validat = [validators.Optional()]

        if "min" in rule: 
            if "max" in rule:
                validat.append (validators.NumberRange (min=int (rule["min"]),
                                                    max=int (rule["max"])))
            else:
                validat.append (validators.NumberRange (min=float (rule["min"])))

        
        fieldtype = rule["type"] # muß definiert sein
        if fieldtype == "list":
            setattr (F, field, SelectField (field, 
                                            default=default,
                                            description=description,
                                            choices=rule["choices"], 
                                            validators=validat))
        elif fieldtype == "head":
            choices = head_choices ()
            setattr (F, field, SelectField (field, 
                                            default=default,
                                            description=description,
                                            choices=choices, 
                                            validators=validat))

        elif fieldtype == "headattr":
            choices = []
            # choices kommen von JS function attribChoices () in newline.html
            setattr (F, field, SelectField (field, 
                                            default=default,
                                            description=description,
                                            choices=choices, 
                                            validate_choice=False))

        elif fieldtype == "command":
            choices = command_choices ()
            setattr (F, field, SelectField (field, 
                                            default=default,
                                            description=description,
                                            choices=choices, 
                                            validate_choice=False))

        elif fieldtype == "file":
            if "subdir" in rule:
                choices = dir_choices (rule["subdir"])
            else:
                choices = rule["choices"]
            setattr (F, field, SelectField (field, 
                                            default=default,
                                            description=description,
                                            choices=choices, 
                                            validators=validat))
        elif fieldtype == "int":
            if default:
                default=int (default)
            setattr (F, field, IntegerField (field,  
                                            default=default,
                                            description=description,
                                            validators=validat))
        elif fieldtype == "decimal":
            if default:
                default=float (default)
            setattr (F, field, DecimalField (field,  
                                            default=default,
                                            description=description,
                                            validators=validat))
        else: #text
            setattr (F, field, StringField (field, 
                                            default=default,
                                            description=description,
                                            validators=validat))

@forms.route ("/csvline", methods=['GET', 'POST'])
def csvline ():
    """ Form zum Erzeugen einer neuen Zeile in csv-Datei 

    nach Anlegen einer Zeile wird editmode auf EDIT geschalten 
    """
    class F(Form):
        pass

    fullname = request.args.get ("name")
    fullname = fullname.replace ('+', os.sep) # '+' in '/' umwandeln
    csvfile = Csvfile (fullname)
    head, subdir = os.path.split ( csvfile.path())
    fieldnames = csvfile.fieldnames()
    
    for field in fieldnames:
        rule = globs.room.layout.rule (subdir + field.lower())
        # option == counter:
        if "option" in rule and rule["option"] == "counter":
            rule["default"] = csvfile.nextint (field)
        # option == heads:
        elif "option" in rule and rule["option"] == "heads" \
                        and "headstring" in session:
            rule["default"] = session["headstring"]

        create_field (F, field, rule)

    form = F (request.form)

    option = request.args.get ("option")
    
    if request.method == 'POST':
        if request.form["submit_button"] != "true": # schließen-Button
            return leave_form ()

        elif    form.validate ():                   # Daten ok
        # print ("Data: ", form.data)
            ret = csvfile.add_lines ([form.data])
            if ret["tablechanged"] == "true":
                evaluate_option (option)
            
            flash (ret["message"], category=ret["category"])
            session["editmode"] = "edit" 
            return leave_form ()
        
        else:                                       # falsche Daten
            session["retry_the_form"] = "true"

    root, subdir = os.path.split (csvfile.path()) 
    if "retry_the_form" not in session:
        session["nexturl"] = request.referrer
    return render_template ("newline.html", shortname=csvfile.shortname(),
                            subdir = subdir,
                            submit_text="erzeugen",
                            form = form, fieldnames=fieldnames)


# @forms.route ("/csvfield")
# def csvfield ():
#     """ Form zum Editieren eines CSV-Felds nach den im Layout definierten Regeln
#     """
#     class F(Form):
#         pass

#     subdir = request.args.get ("subdir")
#     field  = request.args.get ("field")

#     rule = globs.room.layout.rule (subdir + field.lower())
#     create_field (F, field, rule)

#     form = F (request.form)

#     return render_template ("csvfield.html", form = form)
    
# @forms.route ("/csvfieldeval", methods=['POST'])
# def csvfieldeval ():
#     """ Form zum Editieren eines CSV-Felds nach den im Layout definierten Regeln
#     """
#     class F(Form):
#         pass

#     subdir = request.form ["subdir"]
#     field  = request.form ["field"]
#     val    = request.form ["val"]

#     rule = globs.room.layout.rule (subdir + field.lower())
#     create_field (F, field, rule)

#     form = F (request.form)
#     form[field].data = val
#     print ("formdata: ", form.data)
#     result = form.validate ()
#     return "ok"

@forms.route ("/usb/<action>", methods=['GET', 'POST'])
@login_required
def usb (action:str):
    """ Form zur Übermittlung und Auswahl eines USB-Sticks.

    Das Form wird in einem Modal angezeigt. Um nach der Validierung und dem
    anschließenden Seitenaufbau das Modal wieder anzuzeigen, wird eine 
    Sessionvariable modalactive auf 'true' gesetzt.
    action: 'backup', 'backupnew', 'restore', 'dbbackup', 'dbrestore'
    """
    choices = get_usbchoices ()
    # choices = onoff_choices
    # default = "0"
    class Usbform (Form):
        device = SelectField ("USB-Stick wählen", choices=choices)

    usbform = Usbform (request.form)

    if request.method == 'POST' and usbform.validate ():
        usbdrv = usbform.device.data
        session.pop ("modalactive", None)

        if action == "backup":
            msg = globs.room.usbbackup (usbdrv)
        elif action == "backupnew":
            msg = globs.room.usbbackup (usbdrv, neu=True)
        elif action == "restore":
            # nun weiter: Verzeichnis auswählen und restore:
            # mapping vom Stick erzeugen
            # roomviews.py -> restoresource()
            globs.room.usbmapping (usbdrv)
            session["usbdrive"] = usbdrv
            session["usbcheck"] = "true"
            msg = {"message":"Restore angefragt", 
                    "category":"info"} 
        elif action == "dbbackup":
            msg = dbbackup (usbdrv)
        elif action == "dbrestore":
            msg = dbrestore (usbdrv)
        else:
            msg = {"message":"Diese USB-Aktion ist nicht vorgesehen", 
                    "category":"danger"} 

        flash (msg["message"], category=msg["category"])
        return  redirect (redirect_url())

    # Titel:
    if action == "backup":
        title = "Backup auf USB"
        submit_text = "backup"
    elif action == "backupnew":
        title = "leeren Raum (Datenstruktur) auf USB"
        submit_text = "backup"
    elif action == "restore":
        title = "Restore von USB"
        submit_text = "wählen"
    elif action == "dbbackup":
        title = "Benutzer-Datenbank Backup auf USB"
        submit_text = "backup"
    elif action == "dbrestore":
        title = "Restore Benutzer-Datenbank von USB"
        submit_text = "wählen"
    else:
        title = "USB-Aktion"
        submit_text = "schließen"

    # USB Laufwerk vorhanden?
    if choices == []:
        text = "Kein USB-Laufwerk gefunden."
        return render_template ("modaldialog.html", title = title,
                                                body  = "textbody",
                                                text = text)

    session["modalactive"] = "true"
    endpoint = f"/forms/usb/{action}"
    return render_template ("modaldialog.html", title = title,
                                                modalform  = usbform,
                                                endpoint = endpoint,
                                                body  = "formbody",
                                                submit_text = submit_text)


@forms.route ("/modalclose", methods=['POST'])
@login_required
def modalclose ():
    """ Sessionvariable 'modalactive' löschen, wenn Modal
    mit 'X' oder schließen-Button beendet wird
    """
    session.pop ("modalactive", None)
    globs.room.usbmapping (None, remove=True)

    return "ok"
