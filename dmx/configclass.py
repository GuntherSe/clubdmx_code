#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" class Config
shelve wird nicht verwendet, da auf verschiedenen Betriebssaytemen
verschiedene Datenstrukturen. Daher nicht portierbar.
Datenstruktur = Dictionary, gespeichert in CSV Datei. 

"""

# import sys
import os
import os.path
import csv

# if __name__ == '__main__':
from csvfileclass import Csvfile
# else:
#     from .csvfileclass import Csvfile

class Config:
    """ Config Methoden:
get (key): wenn vorhanden, dann value liefern
set (key, value): key:value in dict aufnehmen
"""

    def __init__(self, newname=None):
        if newname:
            self.file = Csvfile (newname)
            # Existenz prüfen:
            if not os.path.isfile (self.file.name()):
                tempcfg = Csvfile ("config")
                tempcfg.backup (self.file.csvname)
        else:
            self.file = Csvfile ("config")
        self._data    = {}
        self._cfields = []
        self.data_ok = False
        self.get_data()

    def open (self, newname:str) ->bool:
        """ neue cfg Datei wählen
        """
        self.file.name (newname)
        self.get_data ()
        return self.data_ok
        

    def get_data (self) -> None:
        """ Daten aus self._file einlesen
        = Data init
        Struktur: Key, Value
        """
        fname = self.file.name()
        self._data.clear ()
        self._cfields.clear ()
        self.data_ok = False

        if os.path.isfile (fname):
            with open (fname, 'r',encoding='utf-8') as cf: # zum Lesen öffnen und einlesen
                reader = csv.DictReader (cf, restval= '')
                self._cfields = reader.fieldnames
                for row in reader:
                    self._data[row["key"]] = row["value"]
                self.data_ok = True
        else:
            # self._cfields = []
            print ("Config Konstruktor: ", fname)

    def save_data (self, newname=None) :
        """ self._data in _file oder newfile schreiben 
        return: None
        """
        if not self._cfields: # kein gültiges file eingelesen?
            print ("Feldnamen nicht definiert")
            return

        fname = self.file.name(newname)
        # print (fname)
        with open (fname, 'w', newline='',encoding='utf-8') as pf:
            writer = csv.writer(pf, delimiter=',')
            # Header schreiben:
            writer.writerow (self._cfields)
            # _data schreiben
            writer.writerows (self._data.items())

   
    def data (self) ->dict:
        return self._data
    
    def get (self, key:str) ->str:
        """ Daten zu 'key' retournieren """
        try:
            wert = self._data[key]
            return wert
        except:
            return ""

    def set (self, key:str, value:str):
        """ key:value in self._data eintragen """
        self._data[key] = value
        

    def remove (self, key:str):
        """ Key aus _data entfernen """
        self._data.pop (key, None)

    

        
# ------------------------------------------------------------------------------
# Unit Test:        

if __name__ == '__main__':
    cfg = Config("app")
    print ("Patch:", cfg.get("patch"))
    print ("Test:", cfg.get("test"))
    print ("leer:", cfg.get("leer"))
    cfg.set("test","123")
    print (cfg.data())
    cfg.save_data()
    # cfg.save_data("conftest")
    
