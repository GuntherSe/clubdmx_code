#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" View zur Config """

import os
import os.path

from flask import Blueprint, render_template, request, redirect 
from flask import url_for, flash, session, make_response
from wtforms import Form, StringField, IntegerField, SelectField
from flask_login import login_required, current_user

import globs

from apputils import redirect_url
from common_views import check_clipboard
from csvfileclass import Csvfile   
from startup import load_config
from formutils import onoff_choices, dir_choices # , head_choices

dataform = Blueprint ("dataform", __name__, url_prefix="/dataform", 
                     static_folder="static", template_folder="templates")


@dataform.route ("/config", methods=['GET', 'POST'])
@login_required
def config ():
    """ Form zu config.csv 
    """
    # Raum:
    room = os.path.basename (globs.room.path ())

    # aktuelle Config:
    cur = globs.cfg.data ()
    patch_choices = dir_choices ("patch")
    cuefader_choices = dir_choices ("cuefader")
    cuebutton_choices = dir_choices ("cuebutton")
    cue_choices = dir_choices ("cue")
    stage_choices = dir_choices ("stage")
    pages_choices = dir_choices ("pages")

    if globs.PYTHONANYWHERE == "false":
        midibutton_choices = dir_choices ("midibutton")

        midiindevices = globs.midi.list_devices ("input")
        midiin_choices = [("-1", "kein Midi-Input")]
        for elem in midiindevices:
            midiin_choices.append ((str(elem[0]), elem[3])) # Namen

        midioutdevices = globs.midi.list_devices ("output")
        midiout_choices = [("-1", "kein Midi-Output")]
        for elem in midioutdevices:
            midiout_choices.append ((str (elem[0]), elem[3])) # Namen
    else:
        # zur simulierten Anzeige im Midi-Tab:
        midibutton_choices = dir_choices ("midibutton")
        midiindevices = [(0,"kein Midi", "input", "in PytonAnywhere nicht verfügbar")]
        midiin_choices = [("-1", "kein Midi-Input")]
        midioutdevices = [(0,"kein Midi", "output", "in PytonAnywhere nicht verfügbar")]
        midiout_choices = [("-1", "kein Midi-Output")]



    class Configform (Form):
        patch        = SelectField ("Patch", choices=patch_choices,
                        default=cur["patch"])
        ola_ip       = StringField  ("OLA-Adresse", default=cur["ola_ip"])
        # universes    = IntegerField ("Universes", default=cur["universes"])
        pages        = SelectField ("Cuelist-Tabelle", choices=pages_choices,
                        default=cur["pages"])
        stage         = SelectField ("Stage", choices=stage_choices,
                        default=cur["stage"])
        cuefaders     = SelectField ("Zusatz-Fader", choices=cuefader_choices,
                        default=cur["cuefaders"])
        cuebuttons    = SelectField ("Zusatz-Buttons", choices=cuebutton_choices,
                        default=cur["cuebuttons"])
        savecuelevels = SelectField ("Levels speichern", choices=onoff_choices,
                        default=cur["savecuelevels"])
        start_with_cue = SelectField ("Starte mit Startcue", choices=onoff_choices,
                        default=cur["start_with_cue"])
        startcue      =  SelectField ("wähle Startcue", choices=cue_choices,
                        default=cur["startcue"])
        exebuttons1   = SelectField ("Executer-Buttons oben", 
                        choices=cuebutton_choices,
                        default=cur["exebuttons1"])
        exebuttons2   = SelectField ("Executer-Buttons unten", 
                        choices=cuebutton_choices,
                        default=cur["exebuttons2"])
        exefaders     = SelectField ("Executer-Fader", 
                        choices=cuefader_choices,
                        default=cur["exefaders"])
    
        # if globs.PYTHONANYWHERE == "false":
        midi_on      = SelectField ("Midi ein/aus", choices=onoff_choices,
                        default=cur["midi_on"])
        midi_buttons = SelectField ("Midi Funktionstasten", choices=midibutton_choices,
                    default=cur["midi_buttons"])
        midi_input_1 = SelectField ("Midi Input 1", choices=midiin_choices,
                        default=cur["midi_input_1"])
        midi_input_2 = SelectField ("Midi Input 2", choices=midiin_choices,
                        default=cur["midi_input_2"])
        midi_input_3 = SelectField ("Midi Input 3", choices=midiin_choices,
                        default=cur["midi_input_3"])
        midi_input_4 = SelectField ("Midi Input 4", choices=midiin_choices,
                        default=cur["midi_input_4"])
        midi_output_1  = SelectField ("Midi Output 1", choices=midiout_choices,
                        default=cur["midi_output_1"])
        midi_output_2  = SelectField ("Midi Output 2", choices=midiout_choices,
                        default=cur["midi_output_2"])
        midi_output_3  = SelectField ("Midi Output 3", choices=midiout_choices,
                        default=cur["midi_output_3"])
        midi_output_4  = SelectField ("Midi Output 4", choices=midiout_choices,
                        default=cur["midi_output_4"])
        osc_input    = SelectField ("OSC Input ein/aus", choices=onoff_choices,
                        default=cur["osc_input"])
        osc_inputport = IntegerField ("OSC Input Port", 
                        default=cur["osc_inputport"])

    configform = Configform (request.form)

    if request.method == 'POST' and configform.validate():
        # request.data in config übertragen und config neu laden:
        for key,val in configform.data.items():
            globs.cfg.set (key, val)
        globs.cfg.save_data ()
        load_config (with_savedlevels=True)
        flash ("Config ok.")
        return  redirect (redirect_url())

    confname = globs.cfg.file.shortname ()
    if "datatab" in session:
        datatab = session["datatab"]
    else:
        datatab = "room-tab"

    # Zusatz-Midibuttons in Tabelle in Midi-Tab anzeigen
    check_clipboard ()
    fname = globs.cfg.get("midi_buttons")
    filename = os.path.join (globs.room.midibuttonpath(),fname)
    csvfile = Csvfile (filename)
    if csvfile.changed():
        changes = "true"
    else:
        changes = "false"

    
    # https://stackoverflow.com/questions/28627324/disable-cache-on-a-specific-page-using-flask
    response = make_response (render_template("data/dataindex.html", 
                    confname = confname,
                    confdata = cur,
                    room = room,
                    datatab = datatab,
                    configform = configform,
                    # Tabellendaten:
                    shortname = csvfile.shortname(),
                    pluspath = csvfile.pluspath(),
                    fieldnames = csvfile.fieldnames(),
                    items = csvfile.to_dictlist(), 
                    changes = changes,
                    option  = "midibutton", 
                    excludebuttons = ["uploadButton", "deleteButton"] 
                ))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response
    

@dataform.route ("/datatab/<active>", methods=['POST'])
def datatab (active:str) -> str:
    """ aktiven Tab pro User in session speichern
    """
    session["datatab"] = active
    return "ok"


