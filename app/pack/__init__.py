#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Grundgerüst für ein package 


from flask import Blueprint

pack = Blueprint ("pack", __name__, url_prefix="/pack", 
                     static_folder="../static", template_folder="templates")

from app.pack import routes