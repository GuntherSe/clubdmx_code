#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import shutil # fürs kopieren
# import json
# import csv
from urllib.parse import unquote
import sys

class Csvname:
    """ Klasse zur Behandlung von Änderungen in CSV-Files:
suche nach fname.ccsv, fname.csv
Auswahl der richtigen Datei
Backup, Sichern
"""
    def __init__(self, newname=None):

        self.CSVEXT = os.extsep + "csv"
        self.CHGEXT = os.extsep + "ccsv"

        # filename ohne .extension, 
        if newname:
            self.PATH, fname = os.path.split (newname)
            if not self.PATH:
                self.PATH = os.path.dirname(os.path.realpath(__file__))
            self._file, ext  = os.path.splitext (fname) 
            # _file = shortname, ohne Endung
            
            fname, ext       = os.path.splitext (newname)
            self.csvname  = os.path.join (self.PATH, self._file) + self.CSVEXT
            self.ccsvname = os.path.join (self.PATH, self._file) + self.CHGEXT
            #print (self.PATH, self._file)
            #print (self.csvname, self.ccsvname)
        else:
            self.PATH     = os.path.dirname(os.path.realpath(__file__))
            self._file    = None 
            self.csvname  = None
            self.ccsvname = None
            #print (self.PATH, "kein CSV-File")
        # print ("Csvname.init: Filename", self._file)    

    def name (self, newname = None):
        """ Filename ändern bzw aktuellen Filenamen retournieren

        voller Pfadname, zuerst .ccsv, dann .csv
        """
        if newname:
            self.__init__ (newname)

        if not self._file:
            return None
        
        if os.path.isfile (self.ccsvname):
            return self.ccsvname
        else:
            return self.csvname

    def shortname (self):
        """ Name ohne Pfad und Endung"""
        return self._file


    def longname (self) -> str:
        """ shortname + .ccsv (geändert) / .csv (keine Änderungen)
        """
        if self.changed():
            return self.shortname() + self.CHGEXT
        else:
            return self.shortname() + self.CSVEXT

    def path (self):
        """ Pfad """
        return self.PATH

    def pluspath (self) ->str:
        """ Pfad mit + statt / """
        return self.PATH.replace (os.sep, '+')

    def exists (self) -> bool:
        """ Existenz prüfen
        True, wenn .ccsv oder .csv existiert
        """
        if os.path.isfile (self.ccsvname) or os.path.isfile (self.csvname):
            return True
        else:
            return False

    def changed (self) -> bool:
        """ prüfen, ob Änderungsdatei vorhanden """
        if os.path.isfile (self.ccsvname): # backup existiert bereits
            return True
        else:
            return False
        
    def backup (self, newname:str="") -> dict:
        """ csv-Datei sichern

        newname vorhanden: self.ccsvname suchen.
            Falls vorhanden -> self.ccsvname in newname.csv umbenennen
            Nicht vorhanden -> self.csvname suchen.
                Falls vorhanden -> self.csvname nach newname.csv kopieren
        newname nicht vorhanden: self.ccsvname suchen. 
                Falls vorhanden -> Backup ok
                nicht vorhanden -> self.csvname nach fname.ccsv kopieren
        return: message, category
        """
        ret = {}
        ret["category"] = "error"
        if not self._file:
            ret ["message"] = "Kein Filename vorhanden"
            return ret

        # newname == self.name?
        origname = os.path.splitext ( self.name() )[0]
        if newname and (os.path.splitext (newname)[0] == origname):
            newname = ""

        if newname:
            newfile, ext = os.path.splitext (newname)
            # newname.ccsv löschen (falls vorhanden):
            backupname = newfile + self.CHGEXT
            try:
                os.remove (backupname)
            except:
                pass
            # newname.csv löschen ist für replace nicht nötig:
            backupname = newfile + self.CSVEXT

            if os.path.isfile (self.ccsvname):
                os.replace (self.ccsvname, backupname)
                ret ["category"] = "success"
                ret ["message"]  = "sichern erfolgreich"
                return ret
            else:
                origname = self.name()
                try:
                    shutil.copy(origname, backupname)
                    ret ["category"] = "success"
                    ret ["message"]  = "sichern erfolgreich"
                    return ret
                except IOError as e:
                    ret ["message"]="Konnte File nicht kopieren (IOError). " + e
                    return ret
                except:
                    ret ["message"]= "Unerwarteter Fehler:"+ sys.exc_info()
                    return ret

        else: # newname == "":
            if os.path.isfile (self.ccsvname): # backup existiert bereits
                ret ["category"] = "success"
                ret ["message"]  = "Sicherung existiert bereits"
                return ret
            else: # backup nicht vorhanden -> csv nach ccsv kopieren
                if os.path.isfile (self.csvname):
                    try:
                        shutil.copy(self.csvname, self.ccsvname)
                        ret ["category"] = "success"
                        ret ["message"]  = "Backup erfolgreich"
                        return ret
                    except IOError as e:
                        ret ["message"]="Konnte File nicht kopieren (IOError). " + e
                        return ret
                    except:
                        ret ["message"]="Unerwarteter Fehler: "+ sys.exc_info()
                        return ret
                else: # csvname existiert nicht
                    ret ["message"] ="Fehler: "+ self.csvname+ " existiert nicht"
                    return ret
        ret ["message"] = "ok?"
        return ret

    def save_changes (self) -> bool:
        """ fname.ccsv in fname.csv umbenennen

        return: True, wenn erfolgreich
        """
        if os.path.isfile (self.ccsvname):    # backup existiert
            if os.path.isfile (self.csvname): # original existiert
                os.remove (self.csvname)
            os.rename (self.ccsvname, self.csvname)
            return True
        else:
            return False
            
    def discard_changes (self) -> bool:
        """ fname.ccsv löschen, falls vorhanden

        return: True, wenn erfolgreich
        """
        if os.path.isfile (self.ccsvname):    # backup existiert
            os.remove (self.ccsvname)
            return True
        else:
            return False

    def remove (self):
        """ .csv und .ccsv Dateien löschen """
        if os.path.isfile (self.ccsvname):    # backup existiert
            os.remove (self.ccsvname)
        if os.path.isfile (self.csvname):    # csv existiert
            os.remove (self.csvname)


    def rename (self, newname:str)  ->str:
        """ csv-Datei umbenennen

        .csv  vorhanden -> .csv umbenennen
        .ccsv vorhanden -> .ccsv umbenennen
        Pfad von newname ignorieren, bleibt im selben Pfad wie self
        return: Fullname:str
        """  
       
        tail = os.path.basename (newname)
        fullname = os.path.join (self.PATH, tail)
        newcsv = Csvname (fullname)
        if self.exists (): # es gibt etwas zum Umbenennen
            # newcsv Datei(en) entfernen
            if os.path.isfile (newcsv.csvname): 
                os.remove (newcsv.csvname)
            if os.path.isfile (newcsv.ccsvname): 
                os.remove (newcsv.ccsvname)
        else: # nichts zum Umbenennen
            return ""
            
        if os.path.isfile (self.csvname):
            shutil.move (self.csvname, newcsv.csvname)
        if os.path.isfile (self.ccsvname):
            shutil.move (self.ccsvname, newcsv.ccsvname)
        # if oldcsv.exists ():
        #     shutil.move (oldcsv.name(), fullname)
        #     oldcsv.remove ()
        self.name (fullname)
        return self.shortname ()
        # TODO: testen testen testen

# -------------------------------------------------------------------------
# Modul Test:

if __name__ == '__main__':

    testfile = "C:\\temp\\jazzitbar.csv"
    zielfile = "C:\\temp\\jazzitbarneu.csv"
    neufile  = "C:\\temp\\neufile.csv"

    infotxt = """
    ---- Csvname Class Test -----
    Kommandos: x = Exit
               # = zeige diese Info
               a = Testfile C:\\temp\\jazzitbar.csv 
               b = Testfile C:\\temp\\app.csv
               c = Zielfile C:\\temp\\jazzitbarneu.csv               
               d = Zielfile C:\\temp\\appneu.csv
               e = Neufile  C:\\temp\\neufile.csv
               f = Neufile  neufile.csv
               g = Neufile  neufile


               1 = Test backup Testfile und Zielfile
               2 = Test backup Testfile -> Zielfile
               3 = Test save_changes des Testfiles
               4 = Test discard_changes des Testfiles
               5 = Prüfen, ob Testfile und Zielfile existieren
               6 = Zielfile entfernen
               7 = Zielfile in 'neufile' umbenennen
    """
    print (infotxt)
    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
            elif i == 'a':
                testfile = "C:\\temp\\jazzitbar.csv"
                print (f"Testfile: {testfile}")
            elif i == 'b':
                testfile = "C:\\temp\\app.csv"
                print (f"Testfile: {testfile}")
            elif i == 'c':
                zielfile = "C:\\temp\\jazzitbar.csv"
                print (f"Zielfile: {zielfile}")
            elif i == 'd':
                zielfile = "C:\\temp\\appneu.csv"
                print (f"Zielfile: {zielfile}")
            elif i == 'e':
                neufile = "C:\\temp\\neufile.csv"
                print (f"Neufile: {neufile}")
            elif i == 'f':
                neufile = "neufile.csv"
                print (f"Neufile: {neufile}")
            elif i == 'g':
                neufile = "neufile"
                print (f"Neufile: {neufile}")

            elif i == '1':
                csvfile = Csvname (testfile)
                ret = csvfile.backup ()
                print ("Testfile: ", ret)
                csvfile.name (zielfile)
                ret = csvfile.backup ()
                print ("Zielfile: ", ret)
                print (f"{testfile} und {zielfile} gesichert.")
                
            elif i == '2':
                csvfile = Csvname (testfile)
                ret   = csvfile.backup (zielfile)
                print (ret)
                print (f"{testfile} als {zielfile} gesichert.")
                
            elif i == '3':
                csvfile = Csvname (testfile)
                ret   = csvfile.save_changes ()
                if ret:
                    print ("ok")
                else: # ändern
                    print ("nichts zu tun")

            elif i == '4':
                csvfile = Csvname (testfile)
                ret   = csvfile.discard_changes ()
                if ret:
                    print (f"ok, Änderungen von {testfile} verworfen")
                else:
                    print (f"nichts zu tun, keine Änderungen in {testfile}")

            elif i == '5':
                csvfile = Csvname (testfile)
                if csvfile.exists ():
                    print (f"{csvfile.name()} existiert.")
                else:
                    print (f"{testfile} nicht vorhanden.")
                csvfile.name (zielfile)
                if csvfile.exists ():
                    print (f"{csvfile.name()} existiert.")
                else:
                    print (f"{zielfile} nicht vorhanden.")

            elif i == '6':
                csvfile = Csvname (zielfile)
                csvfile.remove ()
                print (f"{zielfile} entfernt.")

            elif i == "7":
                csvfile = Csvname (zielfile)
                oldname = csvfile.shortname ()
                ret = csvfile.rename (neufile)
                if ret:
                    print (f"{oldname} in {ret} umbenannt.")
                else:
                    print (f"{oldname} nicht vorhanden, nichts umbenannt.")

            else:
                pass
    finally:
        print ("exit...")
    
