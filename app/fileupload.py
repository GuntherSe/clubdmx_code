#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import shutil


from flask import Blueprint, request, json, render_template
from flask import flash, redirect, url_for, send_from_directory
from flask import current_app as app
from flask import session

from werkzeug.utils import html, secure_filename

from startup import load_config
import globs


upload = Blueprint ("upload", __name__, url_prefix="", 
                   static_folder="static", template_folder="templates")


# --- File Upload --------------------------------------
# siehe: https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/#uploading-files


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in globs.ALLOWED_EXTENSIONS

# --- csv Upload ------------------------------------------
@upload.route ('/uploadcsv')    
@upload.route ('/uploadcsv/<path>')
def uploadcsv (path:str=None) -> str:
    """ Formular für Upload 
    Schritte:
      CSV-Datei auswählen, 
      im Formular anzeigen,
      Upload in Upload-Ordner
      CSV-Tabelle in ensprechenden Ordner kopieren
    """
    if path:
        session['UPLOADPATH'] = path

    ret = render_template ("upload.html", filetype=".csv", 
                    action="/postcsvfile")
    return json.dumps (ret)
    

@upload.route ('/postcsvfile', methods=['GET','POST'])
def postcsvfile ():
    """ File Upload 
siehe test_upload Ordner
"""
    if request.method == 'POST':
        #ret = {}
        # check if the post request has the file part
        # print ("request: ", request.files)
        if 'uploadfile' not in request.files:
            flash ('Kein File zum Upload ausgewählt.')
            return redirect (request.url) #json.dumps (ret)
        fnam = request.files['uploadfile']
        # if user does not select file, browser also
        # submit an empty part without filename
        if fnam.filename == '':
            flash ('Kein File zum Upload ausgewählt.')
            return redirect (request.url) #json.dumps (ret)
        if fnam and allowed_file(fnam.filename):
            filename = secure_filename(fnam.filename)
            uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            fnam.save (uploaded_file)
            
            # Wenn 'UPLOADPATH' -> file in UPLOADPATH verschieben
            if "UPLOADPATH" in session:
                # print ("UPLOADPATH: ", session["UPLOADPATH"])
                dest_path = session["UPLOADPATH"].replace ('+', os.sep)
                dest_file = os.path.join (dest_path, filename)
                if os.path.isfile(dest_file) : # file existiert
                    os.remove (dest_file)
                # .CCSV?
                pre, ext = os.path.splitext (dest_file)
                # print ("splitext: ", ext)
                if ext.lower() == ".csv":
                    chdest_file = pre + ".ccsv" # changed dest_file
                    # print ("CCSV-File:", chdest_file)
                    if os.path.isfile(chdest_file) : # file existiert
                        os.remove (chdest_file)
                    
                shutil.move (uploaded_file, dest_file)
                # print ("copy ", uploaded_file, " to ", dest_file)
                session.pop ("UPLOADPATH")
                
            flash ('File gesichert')
            return redirect (request.url)

    return redirect (request.referrer)


@upload.route ('/uploadroom')    
def uploadroom () -> json:
    """ Formular für Upload 
    """
    ret = render_template ("upload.html", filetype=".zip", 
                    action="/postroomzip")
    return json.dumps (ret)
    

@upload.route ('/postroomzip', methods=['GET','POST'])
def postroomzip ():
    """ File Upload 
siehe test_upload Ordner
"""
    if request.method == 'POST':
        # 1) File speichern
        # check if the post request has the file part
        if 'uploadfile' not in request.files:
            flash ('Kein File zum Upload ausgewählt.')
            return redirect (request.url) 
        fnam = request.files['uploadfile']
        # if user does not select file, browser also
        # submit an empty part without filename
        if fnam.filename == '':
            flash ('Kein File zum Upload ausgewählt.')
            return redirect (request.url) 

        if fnam and allowed_file(fnam.filename):
            filename = secure_filename(fnam.filename)
            uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            fnam.save (uploaded_file)
            
        # 2) zip in room.rootpath() entpacken:
            ret = globs.room.unpack_archive (uploaded_file)
            if ret["extract_dir"] == globs.room.path(): # aktueller Raum?
                load_config (with_savedlevels=True)

            os.remove (uploaded_file)                
            flash (f"{filename} wurde hochgeladen und entpackt.")
            return redirect (request.url)

    return redirect (request.referrer)


