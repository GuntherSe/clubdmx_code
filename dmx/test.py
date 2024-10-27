#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Diverse Tests """

import os
# import os.path
import time
import csv

def px_to_int (s:str) ->int:
    """ 'px' von String Ende abschneiden
    """
    if s.endswith ("px"):
        return int (round (float (s[:-2])))
    else:
        return int (round (float (s)))


def int_to_pix (i:str) ->str:
    """ px an i anhängen """

    s = i.split (sep=".")    
    if not s[0].endswith ("px"):
        return s[0] + "px"
    return s[0]


def check_px (items:list):
    """ Left, Top, Width und Height anpassen
    'px' anhängen
    """
    for item in items:
        if "Left" in item:
            num = item["Left"]
            item["Left"] = int_to_pix (num)
        if "Top" in item:
            num = item["Top"]
            item["Top"] = int_to_pix (num)
        if "Width" in item:
            num = item["Width"]
            item["Width"] = int_to_pix (num)
        if "Height" in item:
            num = item["Height"]
            item["Height"] = int_to_pix (num)
        

pxitems = ["1", "2px", "3 px", "-4px", "5.1px", "6.2"] 
intitems = ["1", "2.1", "3000", "-4.56", "5px", "60000.12px"]           

infotxt = """
---- Lichtpult Cue Test -----

Kommandos: x = Exit
           # = zeige diese Info 

           1 = check px_to_int
           2 = check int_to_px
"""

print (infotxt)
try:
    i = 1
    while i != 'x':
        i = input ("CMD: ")
        if i == '#':
            print (infotxt)
        elif i == '1':
            for item in pxitems:
                print (item, " ", px_to_int(item))
        elif i == '2':
            for item in intitems:
                print (item, " ", int_to_pix(item))
        else:
            pass
finally:
    print ("bye...")
