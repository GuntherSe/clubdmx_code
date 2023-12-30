#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
from socket import gethostname

from flask import Blueprint, request, json, render_template
from flask import flash, redirect, url_for, send_from_directory
from flask import current_app as app
from flask import session

from werkzeug.utils import secure_filename

from startup import load_config
from apputils import standarduser_required, admin_required, redirect_url
import globs


upload = Blueprint ("upload", __name__, url_prefix="", 
                   static_folder="static", template_folder="templates")


# --- File Upload --------------------------------------
# siehe: https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in globs.ALLOWED_EXTENSIONS

# --- csv Upload ------------------------------------------
@upload.route ('/uploadcsv', methods=['GET','POST'])    
@upload.route ('/uploadcsv/<path>', methods=['GET','POST'])
@standarduser_required
def uploadcsv (path:str=None) -> str:
    """ CSV-Datei Upload

    GET: Formular für Upload 
    POST: empfangene Daten verarbeiten:
        CSV-Tabelle in ensprechenden Ordner kopieren
    """
    if request.method == 'POST':
        #ret = {}
        # check if the post request has the file part
        # print ("request: ", request.files)
        if 'uploadfile' not in request.files:
            flash ('Kein File zum Upload ausgewählt.')
            return redirect  (redirect_url()) #(request.url) 
        fnam = request.files['uploadfile']
        # if user does not select file, browser also
        # submit an empty part without filename
        if fnam.filename == '':
            flash ('Kein File zum Upload ausgewählt.')
            return redirect (redirect_url()) #json.dumps (ret)
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
            return redirect  (redirect_url()) #(request.url)

        return redirect  (redirect_url()) #(request.referrer)
    
    if path:
        session['UPLOADPATH'] = path

    ret = render_template ("fileselect.html", 
                            filetype=".csv", 
                            description = "uploadcsv",
                            action="/uploadcsv")
    return json.dumps (ret)
    

@upload.route ('/uploadroom', methods=['GET','POST']) 
@standarduser_required   
def uploadroom () -> json:
    """ Raum (zip) Upload und Daten entpacken
    
    GET: Formular für Upload 
    POST: zip-File in uploads-Ordner empfangen und entpacken
    """
    if request.method == 'POST':
        # 1) File speichern
        # check if the post request has the file part
        if 'uploadfile' not in request.files:
            flash ('Kein File zum Upload ausgewählt.')
            return redirect  (redirect_url()) #(request.url) 
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
            # return redirect (request.url)
            return redirect (redirect_url())

        return redirect (redirect_url())

    ret = render_template ("fileselect.html", filetype=".zip",
                            description = "uploadroom", 
                            action="/uploadroom")
    return json.dumps (ret)
    

@upload.route ('/uploaddb', methods=['GET','POST'])    
@admin_required
def uploaddb () -> json:
    """ User Datenbank Upload und statt aktueller Datenbank verwenden
    
    GET: Formular für Upload 
    POST: zip-File in uploads-Ordner empfangen und entpacken
    """
    if request.method == 'POST':
        # 1) File speichern
        # check if the post request has the file part
        if 'uploadfile' not in request.files:
            flash ('Kein File zum Upload ausgewählt.')
            return redirect  (redirect_url()) #(request.url) 
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
            
        # 2) aktuelle Datenbank löschen und durch neue Datenbank 
        #   ersetzen:
            dest_file = os.path.join (globs.basedir, ".app.db")
            os.remove (dest_file)
            shutil.move (uploaded_file, dest_file)
                
            flash (f"{filename} ist nun die aktuelle User-Datenbank.")
            return redirect (redirect_url())

        return redirect (redirect_url())

    ret = render_template ("fileselect.html", filetype=".db",
                            description = "uploaddb", 
                            action="/uploaddb")
    return json.dumps (ret)

    
@upload.route ("/downloaddb")
# @admin_required
def downloaddb ():
    """ Download der user-Datenbank
    
    eindeutigen Dateinamen erzeugen
    Kopie von '.app.db' in den uploads-Ordner 
    umbenennen auf neuen Namen 
    senden
    """
    appdb = os.path.join (globs.basedir, ".app.db")
    hostname = gethostname ()
    # print ("Hostname: ", hostname)
    destdbname = hostname + os.extsep + "db"
    dst = os.path.join (app.config["UPLOAD_FOLDER"], destdbname)
    if os.path.isfile (dst): # dst existiert
        os.remove (dst)
    shutil.copyfile (appdb, dst)
    flash (f"{destdbname} wurde erzeugt.", category="success")
    
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               destdbname, as_attachment=True)
