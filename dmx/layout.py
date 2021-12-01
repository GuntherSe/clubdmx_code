#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
# import shutil # fürs kopieren


from csvfileclass import Csvfile

def check_float_to_int (val:float) -> str:
    """ prüfen, ob val in int umgewandelt werden kann 
    val: zu prüfende Zahl
    return: str(int(val)) wenn möglich sonst str(val)
    """
    intval = int(val)
    if intval == val:
        return str(intval)
    else:
        return str(val)

class Layout (Csvfile):
    """ Klasse zur Verwaltung der CSV-Dateien eines Raums 
    self._layout ist das Dictionary, das zu 'Subdir-Field' alle Regeln 
    enthält.
    Mit self.line (key) erhält man das zu key erstellte Regel-Dict.
    Mit self.rule erhält man in einem Dict die Parameter zur Erstellung  
      eines Form-Felds in WTForms
    """

    def __init__ (self, newname=None):
        """ Init """
        super().__init__(newname)

        # _layout ermitteln:
        self._layout = {}
        # self._file_function = self.no_files

        lines = self.to_dictlist ()
        for line in lines:
            key = line["Subdir"] + line["Field"]
            self._layout[key.lower ()] = line
        # print ("Layout ok")

    def keys (self) ->list:
        """ die keys aus dem layout liefern """
        return self._layout.keys ()

    def line (self, key:str) ->list:
        """ Layout zu key liefern """
        if key in self._layout.keys():
            return self._layout[key]
        else:
            return []
            
        
    # def rule (self, subdir:str, field:str) ->dict:
    def rule (self, searchstr:str) ->dict:
        """ die Regeln für gewählte Zelle 
        searchstr = subdir + field
        subdir: Unterordner von Room = 1. Spalte in Layout
        field:  Feldname = 2. Spalte in Layout
        subdir und field in Kleinbuschtaben
        """

        # searchstr = subdir + field
        ret = {}
        kwargs = {} # für den Field-Konstruktor
        if searchstr in self._layout:
            # Regeln ermitteln für:
            # label (=Label oder Field):
            row = self._layout[searchstr]
            if "Label" in row and row["Label"] :
                ret["label"] = row["Label"]
            else:
                ret["label"] = row["Field"]
            # value (=Default):
            if "Default" in row and row["Default"] :
                ret["default"] = row["Default"]
            # Placeholder:
            if "Placeholder" in row and row["Placeholder"] :
                ret["placeholder"] = row["Placeholder"]
            # required ?:
            if "Required" in row and row["Required"] :
                ret["required"] = row["Required"]
            # Option:
            if "Option" in row and row["Option"]:
                ret["option"] = row["Option"]

            # type (text,decimal,select) -> unterschiedliche Field-Konstruktoren:
            # type 'head': choices in forms.py ermitteln
            
            fieldtype = row["Fieldtype"]
            ret["type"] = fieldtype
            
            if fieldtype == "list":
                chlist = []
                # values = []
                values = row["Range"].split()
                for val in values:
                    chlist.append ((val,val))
                    # values.append (choice)
                ret["choices"] = chlist # für Form nötig
                ret["values"]  = values
            elif fieldtype == "int":
                # min,max (=Range)
                bereich = row["Range"]
                if len (bereich):
                    ret["min"] , ret["max"] = bereich.split()
            elif fieldtype == "decimal":
                # Range:
                if "Range" in row and row["Range"] == ">=0": # positiv
                    ret["min"] = 0

            elif fieldtype == "file": # file
                if "Option" in row:
                    ret["subdir"] = row["Option"]
                    # ret["choices"] = self.file_function (row["Option"])
                # else:
                #     ret["choices"] = self.file_function ()
            elif fieldtype == "disabled":
                ret["disabled"] = "true"

            if len (kwargs):
                ret["kwargs"] = kwargs
        return ret

    def check (self, key:str, checkval:str) :
        """ Test, ob checkval die Kriterien von layout erfüllt 
        key: Subdir+Field
        checkval: zu überprüfender String
        return: False, wenn nicht bestanden
                checkval
                checkval modifiziert (int statt float)
        """

        if key not in self.keys (): # dann darf editiert werden
            return checkval
        rule = self.rule (key)
        if rule["type"] == "list":
            if checkval in rule["values"]:
                return checkval
            else:
                return False

        elif rule["type"] == "int" or rule["type"] == "head":
            try:
                checkint = int (checkval) 
            except: # kein integer
                # leeres Feld möglich?
                if checkval == '':
                    if "required" in rule:
                        return False
                    else:
                        return checkval
                else:
                    return False

            if "min" in rule.keys () and "max" in rule.keys ():
                try:
                    minimum = int (rule["min"])
                    maximum = int (rule["max"])
                except: # min und max sind keine integer
                    return False
                if minimum <= checkint <= maximum:
                    return checkval
                else:
                    return False
            else: # min und max nicht angegeben
                return checkval

        elif rule["type"] == "decimal":
            try:
                val = float (checkval)
                # return True
            except:
                # leeres Feld möglich?
                if checkval == '':
                    if "required" in rule:
                        return False
                    else:
                        return checkval
                else:
                    return False
            # Range auswerten:
            if "min" in rule.keys ():
                try:
                    minimum = float (rule["min"])
                except: # min ist kein float
                    return False
                if minimum <= val:
                    return check_float_to_int (val) # evtl umwandeln in int
                else:
                    return False
            else: # min 
                return check_float_to_int (val) # evtl umwandeln in int


        else:
            # checkval ist string
            if checkval == '':
                if "required" in rule:
                    return False
                else:
                    return True


    def defaults (self, subdir:str) ->dict:
        """ Defaultwerte zu den Feldern in Subdir als Dict 
        """
        ret = {}
        for key,val in self._layout.items ():
            if val["Subdir"] == subdir:
                ret[val["Field"]] = val["Default"]
        return ret


# -------------------------------------------------------------------------
# Modul Test:

if __name__ == '__main__':

    layout = Layout ("layout")

    print (layout.name())
    print ("Keys: ", layout.keys())

    key = "cuebuttontype"
    print (f"key: {key}, line: {layout.line (key)}")

    print ("Defaults zu 'cuebutton':")
    print (layout.defaults ("cuebutton"))

    chk = layout.check ("cuebuttonmidifader", "123")
    print (f"check cuebutton midifader: {chk}")

    chk = layout.check ("cuebuttonmidiinput", "123")
    print (f"check cuebutton midiinput: {chk}")

    chk = layout.check ("headsize", "1")
    print (f"check head size: {chk}")

    chk = layout.check ("cueheadnr", "10")
    print (f"check cue headnr: {chk}")

    chk = layout.check ("cuebuttonfadein", "10.4 sec")
    print (f"check cuebutton fadein: {chk}")

    chk = layout.check ("cuefaderfilename", "xy 1")
    print (f"check cuefader filename: {chk}")

