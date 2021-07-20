#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import json

from werkzeug.utils import html

# https://stackoverflow.com/questions/33135038/how-do-i-use-os-scandir-to-return-direntry-objects-recursively-on-a-directory

from os import scandir

from flask import render_template

import globs

def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)  # see below for Python 2.x
        else:
            yield entry

def get_curdir (spath:str='.', basedir:str='') ->str:
    """ aus spath (=searchpath) absolut-Pfad erzeugen 
    
    spath = Suchpfad
    basedir = Pfad vor Suchpfad
    z.B.: c:\\data\\basedir\\spath oder spath oder ..
    """
    if basedir:
        if os.path.isabs (basedir):
            cwd = basedir
        else:
            cwd = os.path.abspath (basedir)
    else:
        cwd = os.getcwd()

    if os.path.isabs(spath): # abs. Pfad
        if os.path.isdir (spath):
            return spath
        return cwd

    if spath == '.':
        ret = cwd
    elif spath == '..':
        ret = os.path.dirname (cwd)
    else:
        ret = os.path.join (cwd, spath)

    if (os.path.isdir (ret)):
        return ret
    else:
        return cwd


def list_dir (spath:str="", ftype:str="" ) ->dict:
    """ list directory 'path' mit Dateityp 'ftype'
spath: z.B. '.', 'subdir', ...
ftype: Dateiendung, Groß-/Kleinschreibung egal, '.xyz' oder 'xyz'
return: Dict mit allen Subdirs in Liste, dann alle Dateien in Liste
"""
    dirlist  = []
    filelist = []

    if ftype:
        ftypelow = ftype.lower()
    else:
        ftypelow = ""

    searchdir =  get_curdir(spath)       
    try:
        for entry in scandir (searchdir):
            if entry.is_dir (follow_symlinks=False):
                dirlist.append (entry.name)
            elif ftype == "":
                filelist.append (entry.name)
            elif entry.name.lower().endswith(ftypelow):
                                     # Groß- und Kleinschreibung egal
                filelist.append (entry.name)
    except:
        print ("list_dir: Suchpfad nicht gefunden:", searchdir)
    # dirlist.sort ()
    ret = {}
    ret["basedir"] = searchdir
    ret["dir"] =  sorted (dirlist, key=str.lower)
    ret["file"] = sorted (filelist, key=str.lower)
    
    return ret

def dir_explore (params:str) -> json:
    """ params = json string
basedir: nötig bei spath == '..', absolut-Pfad
spath: Suchpfad, absolut oder relativ=Subdir
ftype: Filetype (groß-klein egal) oder None
updir: erlaubt oder nicht, bool
Return:
basedir: Absolut-Pfad
table: Bootstrap Tabele
"""
    spath = ""
    ftype = ""
    updir = False
    basedir = ""

    #print ("dir_explore params: ", params)
    data = json.loads (params)
    # print (data);
    
    try:
        temp = data["basedir"].replace ('+', os.sep)
        basedir = get_curdir (temp)
    except (ValueError, KeyError, TypeError):
        basedir = get_curdir(globs.room.path())

    try: # spath
        temp = data['spath'].replace ('+', os.sep) # absolut oder relativ
        if os.path.isabs (temp):
            spath =  get_curdir (temp)
        else:
            spath = get_curdir (temp, basedir)
    except (ValueError, KeyError, TypeError):
        spath = basedir
        
    try:
        ftype = data['ftype']
    except (ValueError, KeyError, TypeError):
        pass

    try:
        updir = data['updir']
        if updir == 'true':
            updir = True
        else:
            updir = False
    except (ValueError, KeyError, TypeError):
        pass
    
    ret = {}
    ret['basedir'] = spath
    ret['table']   = dir_to_table (spath,ftype,updir)
    return json.dumps (ret)

def dir_to_table (spath:str=None, ftype:str=None, updir:bool=False) -> html:
    """  Tabelle aus Dir content erzeugen """

    direc = list_dir (spath, ftype)
    if __name__ == "__main__":
        return direc
    else:
        return render_template ("filelist.html", directory=direc, updir=updir)


    
# -------------------------------------------------------------------------
# Modul Test:

if __name__ == '__main__':

    infotxt = """
    ---- Lichtpult Cue Test -----
    Kommandos: x = Exit
               1 = Test scantree
               2 = Test curdir
               3 = Test list_dir
               4 = Test dir_explore
               5 = Test dir_explore
               7 = Test dir_to_table
    """
    print (infotxt)
    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
            elif i == '1':
                tree = scantree (".")
                for item in tree:
                    print (item)
            elif i == '2':
                print (get_curdir ("."))
                print (get_curdir ("static"))
                print (get_curdir (".."))
                direc = "C:\\Users\\Gunther\\OneDrive\\Programmierung\\clubdmx_rooms"
                print (get_curdir (direc))
                
            elif i == '3':
                print ("1", list_dir ("."))
                print ("2", list_dir ("static"))
                print ("3", list_dir (".."))
                print ("4", list_dir ("d:\\"))
                direc = "C:\\Users\\Gunther\\OneDrive\\Programmierung\\clubdmx_rooms"
                print ("5", list_dir (direc))
                print ("")
                print ("6", list_dir (".", "py"))
                print ("7", list_dir ("static\\css", ".css"))
                print ("8", list_dir ("..", ".py"))
                print ("9", list_dir ("static\\css", "txt"))
                direc = "C:\\Users\\Gunther\\OneDrive\\Programmierung\\clubdmx_rooms"
                print ("10", list_dir (direc, ".PY"))
                
            elif i == '4':
                data = '{"basedir":"."} '
                print ("1", dir_explore (data))
                data = '{"basedir":""} '
                ret  = json.loads (dir_explore (data))
                print ("\n2", ret["table"])
                
            elif i == '5':
                data = '{"basedir":"", "spath":"templates", '
                data +='"ftype":"html", "updir":"true"} '
                ret  = json.loads (dir_explore (data))
                print ("basedir:", ret["basedir"], "\ntable:", ret["table"])
                
            elif i == '7':
                s = "."
                u = "true"
                print (dir_to_table (spath=s, updir=u))
                
                spath = "templates"
                ftype = ".html"
                updir = "true"
                print (dir_to_table (spath, ftype, updir))
                
            else:
                pass
    finally:
        print ("exit...")
    
