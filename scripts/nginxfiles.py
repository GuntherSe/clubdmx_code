#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Die Files erzeugen, die für den Start von ClubDMX mit NGINX 
    benötigt werden:
    /etc/systemctl/system/clubdmx.service
    /etc/nginx/sites-enabled/clubdmx
    Diese Files werden entsprechend dem Code-Verzeichnis und dem User 
    angepasst.

    Virtual Environment: wenn argv[1] angegeben, dann ist das der Pfad zur venv
 """

import os
import os.path
import sys

# -------------------------------------------------------------------------

if __name__ == '__main__':

    user = os.getenv ("USER", "pi")
    if os.name == "nt":
        print ("TEST des Scripts. NGINX ist für Windows nicht verfügbar.")
    defaultpath = os.path.dirname (os.path.dirname(os.path.realpath(__file__)))

    codepath = os.getenv ("CLUBDMX_CODEPATH", defaultpath)
    if len (sys.argv) > 1:
        venv = sys.argv[1]
    else:
        venv = None
    print (f"codepath: {codepath}")
    print (f"user: {user}")

    inname = os.path.join (defaultpath, "scripts", "service_proto.txt")
    outname = os.path.join (defaultpath, "scripts", "service.txt")
    with open (inname, 'rt', encoding='utf-8') as infile:
        with open (outname, 'wt', encoding='utf-8') as outfile:
            for line in infile:
                line = line.replace ("_USER", user)
                line = line.replace ("_CLUBDMX_CODEPATH", codepath)
                if venv:
                    venvoption = "-v " + venv
                    line = line.replace ("_VENV", venvoption)
                else:
                    line = line.replace ("_VENV", "")
                outfile.write (line)

    inname = os.path.join (defaultpath, "scripts", "site_proto.txt")
    outname = os.path.join (defaultpath, "scripts", "site.txt")
    with open (inname, 'rt', encoding='utf-8') as infile:
        with open (outname, 'wt', encoding='utf-8') as outfile:
            for line in infile:
                # line = line.replace ("_USER", user)
                line = line.replace ("_CLUBDMX_CODEPATH", codepath)
                outfile.write (line)
    
        

