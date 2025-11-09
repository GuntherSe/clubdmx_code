#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import deque
from threading import Lock
from app import socketio
from flask_socketio import emit
from flask import session

from midiutils import press_cuebutton, midifader_monitor, midi_commandlist

import logging
logger = logging.getLogger ("clubdmx")
# from loggingbase import Logbase

import globs
sync_thread = None
thread_lock = Lock ()

def background_sync ():
    """ Sync clubDMX data """
    while True:
        if globs.sync_data:
            current = globs.sync_data.popleft()
            socketio.emit (current["event_name"], current["data"])
            

@socketio.event
def connect ():
    """ connect with clients """
    global sync_thread
    # global thread_lock
    with thread_lock:
        if sync_thread is None:
            sync_thread = socketio.start_background_task (background_sync)
    emit('after connect',  {"data":"I'm conntected"})

    
@socketio.on('slider value changed')
def slidervalue_changed(message):
    """ Sliderlevel für Cuefader und Cuelistfader über socketio empfangen 
    index ab 1
    """
    # sliders = len (globs.fadertable)
    curslider = message["who"].split(sep='-') # 'slider-1'
    slidertype = message["fadertype"]
    index = int (curslider[1]) 
    # if index in range (sliders):
    level = message["data"]
    if slidertype == "cuefader":
        globs.fadertable[index].level = float(level) / 255
        if globs.PYTHONANYWHERE == "false" and globs.midiactive:
            midifader_monitor ("cuefader", index, int(float(level)/2))
    else: # cuelistfader
        globs.cltable[index].level = float(level) / 255
        
    emit('update slidervalue', message, broadcast=True)

@socketio.on ("cuebutton pressed")
def button_pressed (message):
    """ Cue Button wurde gedrückt 
    index ab 0
    """
    index = int (message["index"])
    press_cuebutton (index)
    # message["status"] = status
    # emit ("update buttonstatus", message, broadcast=True)

# --- Edit/Select Umschaltung ------------------------------------
@socketio.on ("editmode changed")
def editmode_changed (message):
    """ Bearbeitungsmodus: edit/select

    edit: Zellen bearbeiten
    select: Objektauswahl, z.B. Zeile in CSV oder Head in Stage
    """
    # logger.debug (f"SESSION'editmode' = {session['editmode']}")
    emit ("update editmode", message)


