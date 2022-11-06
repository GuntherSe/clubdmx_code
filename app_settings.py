#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""App configuration."""

import shutil
from os import environ, path, mkdir, pathsep
from dotenv import load_dotenv
from datetime import timedelta

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class AppConfig:
    """Set Flask configuration from environment variables."""

    # General Config
    SECRET_KEY = environ.get('SECRET_KEY')
    SESSION_COOKIE_SAMESITE = 'Lax'
    UPLOAD_FOLDER = path.join (basedir, "uploads")
    MAX_CONTENT_LENGTH = 256 * 1024 # 256KB

    if not path.isdir (UPLOAD_FOLDER):
        mkdir (UPLOAD_FOLDER)
    # https://blog.miguelgrinberg.com/post/cookie-security-for-flask-applications
    # SESSION_COOKIE_SECURE = True
    # REMEMBER_COOKIE_SECURE = True

    # Clubdmx config:
    # Raumpfad wird in startup.py ermittelt.
    
    # ROOMPATH  = environ.get ("CLUBDMX_ROOMPATH")
    # PYTHONANYWHERE in wsgi.py setzen!

    # Flask Config
    FLASK_ENV = environ.get("FLASK_ENV")
    if not FLASK_ENV:
        FLASK_ENV = "production"
    PERMANENT_SESSION_LIFETIME = timedelta (days=365)

    # Datenbank:
    if not path.isfile (".app.db"):
        shutil.copy ("_neu.db", ".app.db")

    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or \
        'sqlite:///' + path.join(basedir, '.app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False    

