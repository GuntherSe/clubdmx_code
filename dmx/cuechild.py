#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Topcue 
in Verwendung als Programmer, Speichern von Stage-Eingaben, Ändern von 
Cues in Fader-Tabelle

"""

# import time
import csv

from cue  import Cue
from csvfileclass import Csvfile
# from csv_views import evaluate_option

class Topcue (Cue):

    def __init__ (self, patch):
        Cue.__init__ (self, patch)
        # _cuefields von Default-csv-Tabelle:
        self._cuefields = self.file.fieldnames()
        self.level = 1.0
        # print ("topcue: ", self._cuefields)

    def __repr__(self):
        return "<Topcue {}>".format (self.count)

    def open (self):
        """ ohne Filename! """
        pass


    def get_cuecontent (self):
        """ content aus contrib erzeugen? """
        pass


    def save (self, newname=None):
        """ wenn newname, dann speichern """

        if newname:
            super.save (newname)
        else:
            pass


    def add_item (self, head:str, attrib:str, level:str):
        """ Ändern von Basismethode: 
        
        attype = 'TOP'
        Eintragung in self.content passiert hier
        """
        key = head + '-' + attrib
        attype = "TOP"
        Cue.contrib.add (self.count, key, level, attype)
        self._active = 1
        # in _cuecontent eintragen:
        found = 0
        for row in self.content:
            if row[0] == head and row[1] == attrib:
                # level geändert
                found = 1
                row[2] = level
        if not found:
            self.content.append ([head, attrib, level])

    def clear (self):
        """ self.content und Einträge in contrib löschen """
        
        self.rem_cuemix ()
        del self.content[:]
        self.level = 1.0
        # print ("clear: ", self.content)

    # def to_dictlist (self) ->list:
    #     """ _cuecontent in csvfile.to_dictlist() Format 

    #     Format: [{'HeadNr':'x','Attr':'y','Intensity':'z'}, {...}, {...}]
    #     für die Anzeige in Modaldialog """
        
    #     ret = []
    #     for row in self.content:
    #         line = {}
    #         for i in range (len (self._cuefields)):
    #             line[self._cuefields[i]] = row[i] 
    #         ret.append (line)
    #     return ret

    def to_csv (self, csvfile:Csvfile) ->dict:
        """ Inhalt von self.content in csvfile schreiben 
        return: Message
        """

        csvfile.backup ()
        fname = csvfile.name()
        # File schreiben:
        with open (fname, 'w',encoding='utf-8', newline='') as pf:
            writer = csv.writer (pf)
            writer.writerow (self._cuefields)
            writer.writerows (self.content)

        # evaluate_option ("cue")
        
        shortname = csvfile.shortname()
        ret = {}
        ret["category"] = "success"
        ret["message"]  = f"Topcue in '{shortname}' gespeichert."
        return ret 


    def merge_to_csv (self, csvfile:Csvfile) ->dict:
        """ Inhalt von self.content in csvfile mischen 
        
        in self.content mix erzeugen, dann nach csvfile speichern
        return: Message
        """

        # csvfile in _cuecontent importieren:
        csvlist = csvfile.to_dictlist ()
        hindex = self._cuefields[0] #  = "Head"
        aindex = self._cuefields[1] #  = "Attr"
        lindex = self._cuefields[2] #  = "Level"

        for elem in csvlist:
        # Suche nach line in _cuecontent
            found = 0
            for line in self.content:
                if elem[hindex] == line[0] and elem[aindex] == line[1]:
                    found = 1
            if not found:
                self.content.append ([elem[hindex], elem[aindex], elem[lindex]])

        self.to_csv (csvfile)

        shortname = csvfile.shortname ()
        ret = {}
        ret["category"] = "success"
        ret["message"]  = f"Topcue in '{shortname}' integriert."
        return ret 


    def merge_to_cue (self, secondcue:Cue):
        """ Inhalt von self.content in secondcue schreiben 
        und Contrib updaten
        """

        for line in self.content:
            secondcue.line_to_cuecontent (line)


    def get_snapshot (self):
        """ Aktuelle Contrib-Daten in Topcue mergen/anhängen"""

        snapshot = self.contrib.snapshot ()
        for item in snapshot:
            self.line_to_cuecontent (item)
