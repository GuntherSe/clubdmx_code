#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" class visudata 

Die für den Mix verwendetetn Daten werden für die Anzeige vorbereitet.
Dazu wird per Head ein Datenpaket erzeugt.
"""
import time
from patch import Patch
outputtime = 0

class Visudata ():

    def __init__(self, patch:Patch):
        self.patch = patch
        self.data = {} # dict mit Visudaten pro Head im Mix
        self.output_function = print


    def add_head (self, headnr:str):
        """ add dict entry for head 
        """
        # if head in self.patch.pdict.keys():
        self.data[headnr] = {}

    def remove_head (self, headnr:str):
        """ remove head from data dict 
        """
        self.data.pop (headnr, None)

    def add_headdata (self, headnr:str, key:str, val):
        """ add data dict to head data

        For view we need Intensity, Red, Green, Blue.
        If no LED, then there are defaults for RGB, see patch.color()
        """
        if headnr not in self.data.keys():
            self.add_head (headnr)
        col = self.patch.color (headnr)
        self.data[headnr]["color"] = col

    def remove_headdata (self, headnr, key):
        """ remove key from head data
        """
        if headnr not in self.data.keys():
            return
        self.data[headnr].pop (key, None)

    def clear (self):
        self.data.clear()

    def set_output_function(self, newfunc):
        """ Visu-Daten an output schicken
        """
        self.output_function = newfunc
        

    def view (self, head:str, attrib:str, val:int):
        """ get viewdata, include them into self.data and output 
        """
        global outputtime

        if head not in self.data.keys():
            self.add_head (head)
        self.add_headdata (head, attrib, val)
        # curtime = time.time()
        # if curtime > outputtime + 0.1: # 1/10 sec
            # outputtime = curtime
        self.output_function (head, "color", self.data[head]["color"])
        

