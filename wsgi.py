#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# PYTHONPATH:
# muss vor Aufruf von python gesetzt werden:
# in Linux in ~/.bashrc
# oder beim Start der app mit skript
import sys
import os
import os.path
thispath  = os.path.dirname(os.path.realpath(__file__))

app_path = os.path.join (thispath, "app")
dmx_path = os.path.join (thispath, "dmx")

sys.path.insert (1, app_path)
sys.path.insert (1, dmx_path)

# os.environ["PYTHONANYWHERE"] = "true"

from app import create_app, db
from auth.models import User


app = create_app ()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}    

# --- Main ----------------------------------------------------

if __name__ == "__main__":

    app.run(host='0.0.0.0') #, threaded=True)

