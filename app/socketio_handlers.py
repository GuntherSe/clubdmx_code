#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from collections import deque
from threading import Lock
from app import socketio
from flask_socketio import emit
# from flask import session

from midiutils import press_cuebutton, midifader_monitor, midi_commandlist
from cuelist_utils import cuedata_to_dict
from visudata import Visudata
import time

faderupdate_time = 0

import logging
logger = logging.getLogger ("clubdmx")
# from loggingbase import Logbase

import globs

sync_thread = None
thread_lock = Lock ()

def background_sync ():
    """ Sync clubDMX data for viewing in website"""
    while True:
        while globs.sync_data:
            current = globs.sync_data.popleft()
            socketio.emit (current["event_name"], current["data"])
        time.sleep (0.04)
            

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
    global faderupdate_time
    """ Sliderlevel für Cuefader und Cuelistfader über socketio empfangen 
    index ab 1
    """
    # sliders = len (globs.fadertable)
    curslider = message["who"].split(sep='-') # 'slider-1'
    slidertype = message["fadertype"]
    if slidertype != "masterfader":
        index = int (curslider[1]) 
    # if index in range (sliders):
    level = message["data"]
    if slidertype == "cuefader":
        globs.fadertable[index].level = float(level) / 255
        if globs.PYTHONANYWHERE == "false" and globs.midiactive:
            midifader_monitor ("cuefader", index, int(float(level)/2))
    elif slidertype == "cuelistfader":
        globs.cltable[index].level = float(level) / 255
    else: # masterfader
        globs.Cue.contrib.masterlevel = float(level) / 255

    curtime = time.time()    
    if curtime > faderupdate_time + 0.1: # 1/10 sec
        emit('update slidervalue', message, broadcast=True)


@socketio.on ("get slider position")
def get_sliderposition (message):
    """ get slider position on document.ready 
    """
    ret = {}
    data = []
    slidertype = message["fadertype"]
    if slidertype == "cuefader":
        for item in globs.fadertable:
            data.append (int (item.level * 255))
    elif slidertype == "cuelistfader": 
        for item in globs.cltable:
            data.append (int (item.level * 255))
    else: # masterfader:
        data.append (int (255 * globs.Cue.contrib.masterlevel))
    ret["data"] = data
    ret["fadertype"] = slidertype
    emit ("init slider position", ret) #, broadcast=True)


@socketio.on ("cuebutton pressed")
def button_pressed (message):
    """ Cue Button wurde gedrückt 
    index ab 0
    """
    index = int (message["index"])
    press_cuebutton (index)


# --- Attribute view -----------------------------------------------------

visu = Visudata (globs.patch)

def attribute_view (*viewdata):
    """ Anzeige der Attributdaten auf website mit socketio 
    """
    # logger.debug (f"attribute_view: {viewdata}")
    globs.sync_data.append ({"event_name":"update attribute",
                    "data":{"head":viewdata[0], 
                            "attr":viewdata[1],
                            "val":viewdata[2]}})

visu.set_output_function (attribute_view)    
globs.topcue.contrib.set_viewfunction (visu.view)

# --- Cuedata view ---------------------------------------------------------

# Cuelist.set_vievfunction (cuedata_view)

@socketio.on ("get cuelist data")
def get_cuelist_data (message):
    """ initialize cuelist(s)
    """
    index = int (message["index"])
    # logger.debug (f"index: {index}")
    if index == -1:
        # init data für alle cuelists
        for item in globs.cltable:
            cuedata = item.get_viewdata ()
            emit ("update cueview", cuedata_to_dict (cuedata))
    else:
        cuedata = globs.cltable[index].get_viewdata ()
        emit ("update cueview", cuedata_to_dict (cuedata))

