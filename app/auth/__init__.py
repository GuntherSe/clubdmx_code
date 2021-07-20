#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint

auth = Blueprint ("auth", __name__, url_prefix="/auth", 
                     static_folder="../static", template_folder="templates")

from auth import routes