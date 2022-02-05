#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import shutil # fürs kopieren
import json
import csv
import math
from urllib.parse import unquote

from csvnameclass import Csvname
from sort import natural_keys

class Csvfile (Csvname):
    """ Klasse zur Behandlung von Änderungen in CSV-Files:
suche nach fname.ccsv, fname.csv
Auswahl der richtigen Datei
Backup, Sichern
"""
    clipboard = [] # für alle Csvfile Instanzen

    def __init__(self, newname=None):

        Csvname.__init__ (self, newname)

        # fieldnames:
        fname = self.name()
        if not fname:
            self._fieldnames = []

        elif not os.path.isfile (fname):
            # print ("File nicht gefunden: ", fname)
            self._fieldnames = []
        else:
            with open (fname, 'r',encoding='utf-8',newline='') as pf:
                reader = csv.DictReader (pf, restval= '')
                self._fieldnames = reader.fieldnames

    def fieldnames (self) -> list:
        """ fieldnames aus CSV-Datei auslesen """
        return self._fieldnames


# -----------------------------------------------------------------------------------           
    def write_cell (self, row_num:int, col_num:int, text) -> dict:
        """ CSV-Zelle ändern

        row_num und col_num ab 1
        """
        lines = []
        ret = {}
        ret["tablechanged"] = "false"

        if isinstance(row_num, str):
            row_num = int(row_num)    
        if isinstance(col_num, str):
            col_num = int(col_num)
        
        # file einlesen:
        fname = self.name()

        if os.path.isfile (fname):
            lines = self.to_list ()
            nfields  = len (lines[0])  # number of fields 
            nlines   = len (lines) - 1 # number of lines, -Fieldnames!

            # row_num und col_num prüfen:
            if col_num > nfields:
                ret["category"] = "danger"
                ret["message"] = "IndexError: SpaltenNr > Anzahl Felder"
                return ret

            if row_num > nlines: # Leerzeile erzeugen
                row_num = nlines +1
                emptyline = []
                for cnt in range (nfields):
                    emptyline.append ('')
                lines.append (emptyline)
            
            # Zelle ändern, row_num[0] = fieldnames:
            try: # IndexError row_num abfangen (=neue Zeile)
                old = lines[row_num][col_num-1]
                lines[row_num][col_num-1] = text
                if old == text:
                    ret["category"] = "success"
                    ret["message"] = "" # keine Änderung
                    return ret
            except:
                pass
                
            # ggf. '.ccsv'-Datei erstellen: 
            self.backup()
            fname = self.name ()
            # File schreiben:
            with open (fname, 'w',encoding='utf-8', newline='') as pf:
                writer = csv.writer (pf)
                writer.writerows (lines)
                ret["tablechanged"] = "true"
                ret["category"] = "success"
                ret["message"] = f"Zeile {row_num} Reihe {col_num}(->{text}) gesichert"
                return ret
        else:
            ret["category"] = "danger"
            ret["message"] = "write_cell: {} nicht gefunden".format (fname)
            return ret
            

    def update_line (self, data:dict):
        """ Zeile mit neuen Daten updaten 

        data muss row_num (str, Zeilennummer ab 1) enthalten
        return: True bei Erfolg, False sonst
        Achtung: Erste zeile in current  = fieldnames
        """
        current = self.to_list ()
        if "row_num" in data.keys ():
            line = int (data["row_num"]) 
            if line - 1 in range (len (current)):
                fieldnames = current [0]
                for key in data.keys ():
                    try:
                        index = fieldnames.index (key)
                        current[line][index] = data[key]
                    except:
                        pass

                self.backup()
                fname = self.name ()
                # File schreiben:
                with open (fname, 'w',encoding='utf-8', newline='') as pf:
                    writer = csv.writer (pf)
                    writer.writerows (current)
                return True
        return False


    def add_lines (self, data:list, pos:int=0) -> str:
        """ neue Zeilen in file anhängen

        data: [{field-1:data-1-1, field-2:data-1-2, ...},
               {field-1:data-2-1, field-2:data-2-2, ...},
               ... ]
        pos: 0 (default):  append
             Zahl:         insert, wenn Zahl < Anzahl Zeilen
        Schritte:
        - backup
        - Daten von Dict -> list
        - csv-File einlesen, list an pos einfügen, speichern
        - keys, die nicht in fieldnames sind, werden ignorert
        """
        def dict_to_list (data:dict) ->list:
            # Hilfsfunktion zur Erzeugung einer neuen Zeile:
            newline = []
            # data-dict -> neue Zeile
            for field in self._fieldnames:
                if field in data:
                    try:
                        content = unquote (data[field])
                    except:
                        content = data[field]
                    newline.append (content)
                else:
                    newline.append ('')
            return newline

        ret = {} 
        self.backup()

        lines = self.to_list () # aktuelle Tabelle
        nlines = len (lines)


        if pos and pos < nlines:
            for dline in reversed (data):
                newline = dict_to_list (dline)
                lines.insert (pos, newline)
        else:
            for dline in data:
                newline = dict_to_list (dline)
                lines.append (newline)

        # File schreiben:
        fname = self.name()
        with open (fname, 'w',encoding='utf-8', newline='') as pf:
            writer = csv.writer (pf)
            writer.writerows (lines)

        # message:
        newlines = len (data)
        ret["tablechanged"] = "true"
        ret["category"] = "success"
        if newlines == 0:
            ret["message"] = "Keine Daten für neue Zeilen."
            ret["category"] = "info"
        elif newlines == 1:
            ret["message"] = "Eine neue Zeile eingefügt."
        else:
            ret["message"] = f"{newlines} neue Zeilen eingefügt."

        return ret


    # def clipboard_data (self) ->bool:
    #     """ clipboard enthält Daten -> True """
    #     if len (Csvfile.clipboard):
    #         return True
    #     else:
    #         return False

    def add_clipboard (self, pos:int=0) ->dict:
        """ Clipboard an pos in csv-File einfügen 
        return: Message
        """

        ret = self.add_lines (Csvfile.clipboard, pos)
        return ret
        

    def line_to_clipboard (self, line:list):
        """ Zeile 'line' an clipboard anhängen 

        clipboard Struktur: [{field-1:val-1-1,field-2:val-1-2,...}
                             {field-1:val-2-1,field-2:val-2-2,...}
                             ... ]
        """
        dl = {} # dictline
        # fieldnames = self.fieldnames ()
        for i in range (len(line)):
            dl[self._fieldnames[i]] = line[i]
        Csvfile.clipboard.append (dl)


    def remove_lines (self, dellines:list) ->dict:
        """ Zeilen aus csv-Datei löschen

        dellines: Liste mit Zeilennummern ab 0
        vorher backup
        return: Message
        """
        self.backup ()
        currentlist = self.to_list ()
        fname = self.name()
        # löschen:
        Csvfile.clipboard.clear ()
        # erste Zeile in currentlist == fieldnames!
        with open (fname, 'w',encoding='utf-8', newline='') as pf:
            writer = csv.writer (pf)
            for i in range (len(currentlist)):
                if i-1 in dellines:
                    self.line_to_clipboard (currentlist[i])
                else:
                    writer.writerow (currentlist[i])
        numlines = len (dellines)

        # message:
        ret = {} 
        if numlines == 1:
            ret["message"] = "1 Zeile gelöscht."
        else:
            ret["message"] = f"{numlines} Zeilen gelöscht."
        ret["tablechanged"] = "true"
        ret["category"] = "success"
        return ret


    def copy_to_clipboard (self, lines:list) ->dict:
        """ Zeilen aus csv-Datei in clipboard kopieren

        lines: Liste mit Zeilennummern ab 0
        return: Message
        """
        currentlist = self.to_list ()
        # clipboard löschen:
        Csvfile.clipboard.clear ()
        # erste Zeile in currentlist == fieldnames!
        for i in range (len(currentlist)):
            if i-1 in lines:
                self.line_to_clipboard (currentlist[i])

        # message:
        numlines = len (lines)
        ret = {} 
        if numlines == 0:
            ret["message"] = "Keine Zeilen ausgewählt."
        elif numlines == 1:
            ret["message"] = "1 Zeile kopiert."
        else:
            ret["message"] = f"{numlines} Zeilen kopiert."
        # ret["tablechanged"] = "true"
        ret["category"] = "success"
        return ret


    def to_list (self) ->list:
        """ CSV-Inhalt in Liste, list pro Zeile

        Zeile: [val-1, val2, ...]
        Output: [[fieldname-1,fieldname-2,...]
                 [val-1-1,val1-2,...]
                 [val-2-1,val-2-2,...]
                 ...
                 [val-n-1,val-n-2,...] ]
        """
        lines = []
        # file einlesen:
        fname = self.name()
        if os.path.isfile (fname):
            with open (fname, 'r',encoding='utf-8', newline='') as pf:
                reader = csv.reader (pf)
                lines = list(reader)
                lines = list (filter (None, lines)) # leere Zeile
        # https://stackoverflow.com/questions/3845423/remove-empty-strings-from-a-list-of-strings

        return lines


    def to_dictlist (self) -> list:
        """ CSV-Inhalt in Liste, dict pro Zeile 

        Zeile: {fieldname-1:value-1, ...}
        Output: [{field_1:val-1-1, field_2:val-1-2, ...},
                {field_1:val-2-1, field_2:val-2-2, ...},
                ...
                {field_1:val-n-1, field_2:val-n-2, ...} ]
        """
        csvlist = []
        # file einlesen:
        fname = self.name()
        if os.path.isfile (fname):
            with open (fname, 'r',encoding='utf-8',newline='') as pf:
                reader = csv.DictReader (pf, restval= '')
                for row in reader:
                    csvlist.append (dict (row))
        return csvlist


    def find (self, search:dict) -> int:
        """ Position der ersten Zeile, die alle keys enthält
        keys: Liste aus key,val-Einträgen, die erfüllt werden müssen
        return: position in csv, kompatibel zu add_lines
        """
        content = self.to_dictlist ()
        matching_keys = search.keys() & self.fieldnames ()
        keycount = len (matching_keys)
        pos = 0
        for line in content:
            matching_values = [k for k in matching_keys if search[k] == line[k]]

            if matching_values and len (matching_values) == keycount:
                return pos 
            else:
                pos = pos + 1

        return -1
            

    def col_edit (self, col:int, newval:str) -> dict:
        """ Spalte editieren 
        col: Spaltennummer
        newval: neuer Wert für Zellen
        """
        ret = {}
        if 0 <= col < len (self._fieldnames):

            current = self.to_list ()
            num_lines = len (current) -1 # Anzahl Zeilen ohne fieldnames
            for line in range (num_lines):
                current[1+line][col] = newval
            self.backup ()
            with open (self.name(), 'w',encoding='utf-8', newline='') as pf:
                writer = csv.writer (pf)
                writer.writerows (current)
            ret["category"] = "success"
            ret["message"] = f"Neuer Wert für '{self._fieldnames[col]}':  {newval}. "
        else:
            ret["category"] = "danger"
            ret["message"] = f"'{col}' außerhalb des gültigen Bereichs."
        return ret


    def nextint (self, field:str) -> str:
        """ nächste Integer in Spalte 'field' finden 
        """
        try:
            col = self._fieldnames.index (field)
        except:
            return '0'
        
        content = self.to_list ()
        intvals = []
        for line in content:
            try:
                val = float (line[col])
                intvals.append (val)
            except: # nicht in int umwandelbar
                pass
        
        if len (intvals):
            ret = math.floor (max (intvals)) +1
            return str (ret)
        else:
            return '1'


    def sort (self, field:str) -> dict:
        """ CSV-Date nach Feld 'field' sortieren
        
        field: Feldname
        return: {message:str, category:str}
        """
        ret = {}
        content = self.to_list ()
        content.pop (0) # fieldnames
        if field in self._fieldnames:
            num = self._fieldnames.index (field)
            sortlist = sorted (content, key=lambda x: natural_keys (x[num]))

            self.backup ()
            fname = self.name()
            with open (fname, 'w',encoding='utf-8', newline='') as pf:
                writer = csv.writer (pf)
                writer.writerow (self._fieldnames)
                writer.writerows (sortlist)

            ret["message"]  = f"{self.shortname()} nach {field} sortiert."
            ret["category"] = "success"
        else:  
            ret["message"]  = f"{field} ist nicht in Feldnamen."
            ret["category"] = "error"

        return ret



# -------------------------------------------------------------------------
# Modul Test:

if __name__ == '__main__':
    infotxt = """
    ---- Csvfile Class Test -----
    Kommandos: x = Exit
               # = zeige diese Info
               5 = Test write_cell
               6 = Test add_lines
               7 = Test remove_lines
               8 = Test find
               9 = Test sort (Name)
              10 = Test sort (Nummer)
    """
    testfile = "C:\\temp\\jazzitbar.csv"
    print (infotxt)
    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
            elif i == '5':
                zeile  = input ("Zeile: ")
                spalte = input ("Spalte: ")
                csvfile = Csvfile (testfile)
                res   = csvfile.write_cell (zeile,spalte,"Neuer Text")
                if res:
                    print (res)

            elif i == '6':
                csvfile = Csvfile (testfile)
                data = [{"Nummer":"11","Text":"Zeile-11","Level":"0"},
                        {"Nummer":"12","Text":"Zeile-12","Level":"100", "x":"y"}]
                pos = input ("Position: ")
                if pos:
                    pos = int(pos)
                res   = csvfile.add_lines (data, pos)
                if res:
                    print (res)

            elif i == '7':
                csvfile = Csvfile (testfile)
                pos = input ("Zeilennummer (Zählung ab 1): ")
                res   = csvfile.remove_lines ([int(pos) - 1])
                if res:
                    print (res)

            elif i == '8':
                csvfile = Csvfile ("c:\\Temp\\led stripe.csv")
                search = {"Text":"Hellgrün","Filename":"hellgrün"}
                found = csvfile.find (search)
                print ("gefunden 1: ", found)
                search2 = {"Text":"ellgrün","Filename":"hellgrün"}
                found = csvfile.find (search2)
                print ("gefunden 2: ", found)

            elif i == '9':
                csvfile = Csvfile (testfile)
                ret = csvfile.sort ("Text")
                print (ret)
            elif i == '10':
                csvfile = Csvfile (testfile)
                ret = csvfile.sort ("Nummer")
                print (ret)

            else:
                pass
    finally:
        print ("exit...")
    
