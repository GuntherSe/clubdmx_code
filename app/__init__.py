#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
# from logging.handlers import RotatingFileHandler
from loggingbase import Logbase

import os
import globs

from threading import Thread
from datetime import date 

from flask import Flask, session #, json, request
from flask_socketio import SocketIO #, emit

from startup_levels import autosave_cuelevels
from startup import load_config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Melde dich an.'

socketio = SocketIO ()

def create_app (test_config=None):
        
    app = Flask(__name__,  instance_relative_config=True)
    # globale Variablen von app.config erhalten:
    app.config.from_object ("app_settings.AppConfig")
    socketio.init_app (app, cors_allowed_origins="*",
                        always_connect=True,async_mode="threading")
                        # #, logger=True, engineio_logger=True)


    # Ausnahme PYTHONANYWHERE: 
    # hier auswerten, damit startup funktioniert.
    val = os.environ.get ("PYTHONANYWHERE") 
    if val: 
        globs.PYTHONANYWHERE = val
        app.config["PYTHONANYWHERE"] = val
    else:
        globs.PYTHONANYWHERE = "false"
        app.config["PYTHONANYWHERE"] = "false",

    # User-Datenbank:
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    
    # Blueprints:
    from basic_views import basic
    from common_views import common
    from cuelist_views import clview
    from csv_views import csvview
    from csvcutpaste import csvcutpaste
    from dataform import dataform
    from data_views import data
    from forms import forms
    from fileupload import upload
    from log_views import logbp
    from patchform import patchform
    from room_views import room
    from stage import stage
    from cue_views import cueview
    from cuechild_views import cuechild
    from auth import auth
    # from pack import pack

    app.register_blueprint (basic)
    app.register_blueprint (common)
    app.register_blueprint (clview)
    app.register_blueprint (csvview)
    app.register_blueprint (csvcutpaste)
    app.register_blueprint (data)
    app.register_blueprint (dataform)
    app.register_blueprint (forms)
    app.register_blueprint (logbp)
    app.register_blueprint (upload)
    app.register_blueprint (patchform)
    app.register_blueprint (room)
    app.register_blueprint (stage)
    app.register_blueprint (cueview)
    app.register_blueprint (cuechild)
    app.register_blueprint (auth)
    # app.register_blueprint (pack)

    # print ("app.url_map: ", app.url_map)

    # logging, siehe:
    # https://github.com/miguelgrinberg/microblog/blob/v0.15/app/__init__.py
    if not app.debug and not app.testing:
        baselogger = Logbase ()
        file_handler = baselogger.filehandler ("clubdmx.log")
        app.logger.addHandler(file_handler)
        # app.logger.setLevel(baselogger.loglevel)
        # app.logger.info('ClubDMX start APP')

    @app.context_processor
    def inject_topcue_content ():
        """ Status des topcue in html-Seiten verfügbar machen 
        """
        if globs.topcue.active ():
            return dict (topcue_content="true")
        else:
            return dict (topcue_content="false")

    @app.context_processor
    def inject_now ():
        """ Datum in html verfügbar machen 
        """
        return {'now': date.today()} 

    @app.before_request
    def make_session_permanent():
        session.permanent = True


    load_config ()

    if globs.PYTHONANYWHERE == "false":
        # in PYTHONANYWHERE keine Threads!
        # Auto-Save Cuelevels:
        save_thread = Thread(target=autosave_cuelevels, daemon=True)
        # save_thread.setDaemon (True)
        save_thread.start()

        print("Sende an OLA-Device: {0}".format (globs.ola.ola_ip))
        globs.ola.start_mixing()

    return app


