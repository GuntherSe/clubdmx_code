#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path

# https://stackoverflow.com/questions/33135038/how-do-i-use-os-scandir-to-return-direntry-objects-recursively-on-a-directory

try:
    from os import scandir
except ImportError:
    from scandir import scandir  # use scandir PyPI module on Python < 3.5


def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)  # see below for Python 2.x
        else:
            yield entry

def list_dir (spath, ftype=None):
    """ list directory 'path' mit Dateityp 'ftype'
spath: z.B. '.', 'subdir', ...
ftype: Dateiendung, Groß-/Kleinschreibung egal
return: Dict mit allen Subdirs in Liste, dann alle Dateien in Liste
"""
    dirlist  = []
    filelist = []
    cwd = os.getcwd()
    if ftype:
        ftypelow = ftype.lower()
        
    # absoluter oder relativer Pfad?
    if os.path.isabs(spath): # abs. Pfad
        searchdir = spath
    else:
        searchdir = os.path.join (cwd, spath)

    for entry in scandir (searchdir):
        if entry.is_dir (follow_symlinks=False):
            dirlist.append (entry.name)
        elif ftype == None:
            filelist.append (entry.name)
        elif entry.name.lower().endswith(ftypelow):
                                              # Groß- und Kleinschreibung egal
            filelist.append (entry.name)
    ret = {}
    ret["dir"] = dirlist
    ret["file"] = filelist
    return ret    

if __name__ == '__main__':
    
    dirlist  = []
    filelist = []
    cuedir = os.path.join (os.getcwd(), "cue")
    print ("cuedir", cuedir)
    
    for entry in scandir ("cue"): # Unterordner vom aktuellen dir
        if entry.is_dir (follow_symlinks=False):
            dirlist.append (entry.name)
            #print ("Dir:", entry.name)
        elif entry.name.lower().endswith(".csv"): # Groß- und Kleinschreibung
            filelist.append (entry.name)
            #print (entry.name)
    print ("Dir:", dirlist)
    print ("Files:", filelist)

    print ("list_dir 1:", list_dir (".", ".py"))
    print ("list_dir 2:", list_dir ("cue", ".CSV"))
    print ("list_dir 3:", list_dir ("D:\\home\\Gunther\\Dokumente\\_files",
                                    ".csv"))
    print ("list_dir 4:", list_dir ("D:\\home\\Gunther\\Dokumente\\"))
    
    
