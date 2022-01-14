#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from csv import DictWriter
import os
import os.path
import shutil # fürs kopieren
from pathlib import Path

import mount
from layout import Layout



# https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth/31039095
def copytree(src, dst, symlinks=False, ignore=None):
    """ Verzeichniskopie
    vorhandene Files werden ersetzt
    """
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if os.path.exists (d):
                os.remove (d)
            shutil.copy (s, d)

            # if not os.path.exists(d):
                # shutil.copy2(s, d)


class Roombase:
    """ Klasse zur Raumverwaltung:

    Raum ist ein Verzeichnis mit Unterordnern, die die Daten für Patch, Cue,
    Config  etc. enthalten. 
    """
    subdirs = ["config", "cue", "cuebutton", "cuefader", "cuelist",
               "head", "midibutton", "pages", "patch", "stage"]

    def __init__(self, newpath=None):

        self.codepath = os.path.dirname(os.path.realpath(__file__))
        if newpath:
            self.PATH = os.path.normpath (newpath)
        else:
            self.PATH = self.codepath
        
        # Raum-Layout
        self.layout = Layout ("layout")
        
        # ist PATH korrekt angelegt?
        self.check()


    def set_path (self, newpath=None):
        """ neues Raumverzeichnis festlegen
        newpath: voller Pfad
        """
        if newpath:
            self.PATH = os.path.normpath (newpath)
        return self.check ()


    def path (self):
        """ Raumverzeichnis liefern """
        return self.PATH

    def name (self):
        """ Raumname liefern"""
        return os.path.basename (self.PATH)

    def rootpath (self):
        """ eine Verzeichnisebene über self.PATH """
        return os.path.dirname (self.PATH)

    
    def configpath (self):
        """ Verzeichnis für Config liefern """
        return os.path.join (self.PATH, "config")


    def cuepath (self):
        """ Verzeichnis für Cue liefern """
        return os.path.join (self.PATH, "cue")

    def cuebuttonpath (self):
        """ Verzeichnis für Cuebutton liefern """
        return os.path.join (self.PATH, "cuebutton")


    def cuefaderpath (self):
        """ Verzeichnis für Cuefader liefern """
        return os.path.join (self.PATH, "cuefader")

    def cuelistpath (self):
        """ Verzeichnis für Cuelist liefern """
        return os.path.join (self.PATH, "cuelist")

    def midibuttonpath (self):
        """ Verzeichnis für Midibutton liefern """
        return os.path.join (self.PATH, "midibutton")

    def pagespath (self):
        """ Verzeichnis für Cuelist-Pages liefern """
        return os.path.join (self.PATH, "pages")


    def stagepath (self):
        """ Verzeichnis für Stage liefern """
        return os.path.join (self.PATH, "stage")


    def usbmap (self):
        """ USB-Mapping Pfad liefern für usb-Restore
        """
        return os.path.join (self.rootpath(), ".usbmap")


    def check (self):
        """ PATH auf Korrektheit prüfen
        """
        ret = {}

        # existiert PATH?
        if not os.path.isdir (self.PATH):
            try:
                os.makedirs (self.PATH)
            except OSError as err:
                message = f"Raum check, Fehler: {err}"
                ret["message"] = message
                ret["category"]="danger"
                # raise OSError (message)
                return ret

            for subdir in self.subdirs:
                os.mkdir (os.path.join (self.PATH, subdir))
            # ret["category"]= "success"
            # ret["message"] = "check ok"
            # return ret

        else: # subdirs prüfen und ggf erzeugen
            for subdir in self.subdirs:
                path = os.path.join (self.PATH, subdir)
                if not os.path.isdir (path):
                    try:
                        os.mkdir (path)
                    except OSError as err:
                        message = f"Raum check, Fehler: {err}"
                        ret["message"] = message
                        ret["category"]="danger"
                        # raise OSError (message)
                        return ret

        if self.PATH != self.codepath: # neuer Raum
            # _neu.csv Files kopieren:
            for subdir in self.subdirs:
                src = os.path.join (self.codepath, subdir, "_neu.csv")
                dst = os.path.join (self.PATH, subdir, "_neu.csv")
                shutil.copy2 (src, dst)
            # Heads von codepath in Raum kopieren
            src = os.path.join (self.codepath, "head")
            dst = os.path.join (self.PATH, "head")
            copytree (src, dst)

        ret["category"]= "success"
        ret["message"] = "check ok"
        return ret

    def rename (self, newname:str):
        """ Raumverzeichnis umbenennen
        Rest vom Pfad bleibt gleich
        wird nur ausgeführt, wenn newname nicht existiert
        newname: ohne Pfad
        """
        ret = {}

        if self.PATH != self.codepath: # codepath nicht umbenennen
            # cwd = os.getcwd()
            # path, src = os.path.split (self.PATH)    
            dst = os.path.join (self.rootpath(), newname)
            if os.path.isdir (dst): # existiert bereits
                ret["category"]="danger"
                ret["message"] = f"Raum existiert bereits: {newname}"
                return ret
            # os.chdir (path)

            try:
                shutil.move (self.PATH, dst)
                self.set_path (dst)
                ret["category"]="success"
                ret["message"] ="rename ok"
            except:
                ret["category"]="danger"
                ret["message"] = "Raum konnte nicht umbenannt werden."
            return ret
            
        ret["category"]="danger"
        ret["message"] = "Raum konnte nicht umbenannt werden."
        return ret
            

    def empty (self):
        """ Raumverzeichnis und Unterordner löschen

        anschließend leeren Raum erzeugen
        """
        if self.PATH != self.codepath: # codepath nicht löschen
            shutil.rmtree (self.PATH, ignore_errors=True)
            # input ("weiter... <enter>")
            return self.check()


    def new_room (self, dest:str) -> dict:
        """ neuen Raum in dest erzeugen:

        subdirs nach dest kopieren 
        dest: voller Pfad
        return: Message
        """
        ret = {}
        if dest!=self.PATH and dest!=self.codepath:
            if os.path.isdir (dest):  
                # existiert bereits, entfernen:
                shutil.rmtree (dest, ignore_errors=True)
            os.makedirs (dest)
            newroom = Roombase (dest)
            ret["category"]="success"
            ret["message"] = f"neuer Raum in {dest} erzeugt."
        else:
            ret["category"]="danger"
            ret["message"] = f"neuer Raum nicht erzeugt. (= aktueller Raum)"
        return ret


    def headupdate (self):
        """ Heads von PATH in codepath kopieren 
        """
        src = os.path.join (self.PATH, "head")
        dst = os.path.join (self.codepath, "head")
        copytree (src, dst)
        

    def backup (self, dest:str) ->dict:
        """ Raumtkopie in dest erzeugen
        dest: Raumpfad, volle Pfadangabe
        return: Message
        """
        ret = {}
        if dest != self.PATH and dest != self.codepath:
            if os.path.isdir (dest):  
                # existiert bereits, entfernen:
                shutil.rmtree (dest, ignore_errors=True)
            os.makedirs (dest)
            for subdir in self.subdirs:
                src = os.path.join (self.PATH, subdir)
                dst = os.path.join (dest, subdir)
                copytree (src, dst)

            ret["category"]="success"
            ret["message"] = f"Backup in {dest} erzeugt."
        else:
            ret["category"]="danger"
            ret["message"] = f"Backup nicht erzeugt. (Ziel = aktueller Raum)"
        return ret


    def restore (self, source:str):
        """ Raumkopie von source kopieren

        prüfen, ob alle subdirs existieren.
        source: voller Pfad
        aktuelle subdirs nicht leeren
        """
        ret = {}
        ret["category"]="danger"
        if self.PATH == self.codepath:
            ret["message"] = f"Restore nicht durchgeführt. (Ziel = CODE-Pfad)"
            return ret

        if not os.path.isdir (source):  
            ret["message"] = f"Restore nicht durchgeführt. ({source} nicht gefunden.)"
            return ret

        for subdir in self.subdirs:
            src = os.path.join (source, subdir)
            if (os.path.isdir (src)):
                dst = os.path.join (self.PATH, subdir)
                copytree (src, dst)

        ret["category"]="success"
        ret["message"] = f"Restore von {source} ok."
        return ret


    def remove (self, dest:str):
        """ externen Raum löschen 
        dest: voller Pfad
        """
        ret = {}
        # path = self.rootpath ()  
        # dest = os.path.join (path, newname)
        if os.path.isdir (dest) and dest!=self.PATH and dest!=self.codepath: 
            shutil.rmtree (dest, ignore_errors=True)
            ret["category"]= "success"
            ret["message"] = f"löschen von {dest} ok."
        else:
            ret["category"]= "danger"
            # Grund angeben fürs nicht Löschen:
            if dest==self.PATH or dest==self.codepath:
                ret["message"] = f"{dest} wurde nicht gelöscht (aktueller Raum)."
            else:
                ret["message"] = f"{dest} ist nicht vorhanden."

        return ret


    def usbbackup (self, dest:str, neu:bool=False) -> dict:
        """ Backup auf USB-Laufwerk
        wie self.backup(), plus mount und unmount
        'neu': leeren Raum auf USB-Laufwerk anlegen
        dest: USB-Pfad
        return: Message
        """
        print ("Dest: ", dest)
        mount.mnt.mount (dest)
        mediapath = mount.mnt.get_media_path (dest)
        print ("Mediapath: ", mediapath)
        if neu:
            backuproom = Roombase ()
            destpath = os.path.join (mediapath, "clubdmx_backup", "_neu")
        else:
            backuproom = Roombase (self.PATH)
            destpath = os.path.join (mediapath, "clubdmx_backup", self.name())
        print ("Pfad: ", destpath)
        backupdir = os.path.normpath (destpath)
        print ("Backupdir: ", backupdir)
        try:
            ret = backuproom.backup (backupdir)
        except:
            ret = {"message":"Backup nicht gelungen", 
                    "category":"danger"} 
        mount.mnt.unmount (dest)
        return ret


    def usbmapping (self, usbdrv:str, remove=False):
        """ Backupstruktur in .usbmap nachbilden

        Für jedes Backup eine Datei in .usbmap anlegen,
        zur Auswahl mit filedialog
        usbdrv: Laufwerk
        remove: .usbmap entfernen
        """
        dst = self.usbmap ()
        # print ("Map-Pfad: ", dst)
        if remove==True:
            if os.path.exists(dst) and os.path.isdir(dst):
                shutil.rmtree(dst)    
        else:
            mount.mnt.mount (usbdrv)
            mediapath = mount.mnt.get_media_path (usbdrv)
            src = os.path.join (mediapath, "clubdmx_backup")
            if not os.path.exists(dst):
                os.makedirs(dst)

            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    Path (d).touch ()
            mount.mnt.unmount (usbdrv)


    def usbrestore (self, usbdrv:str, roomname:str) -> dict:
        """ Restore von USB
        vorhandene Dateien werden überschrieben.
        Raum wird NICHT vorher geleert, daher bewirkt usbrestore 
        ein Ergänzen des Raums
        usbdrv: Laufwerk
        roomname: String
        return: Message
        """
        print (f"USB: {usbdrv}, Raum: {roomname}")
        mount.mnt.mount (usbdrv)
        mediapath = mount.mnt.get_media_path (usbdrv)
        srcpath = os.path.join (mediapath, "clubdmx_backup", roomname)
        # print ("Pfad: ", destpath)
        restoredir = os.path.normpath (srcpath)
        print ("Restoredir: ", restoredir)
        try:
            ret = self.restore (restoredir)
        except:
            ret = {"message":"Restore nicht gelungen", 
                    "category":"danger"} 
        mount.mnt.unmount (usbdrv)
        self.usbmapping (usbdrv, remove=True)
        return ret



# -------------------------------------------------------------------------
# Modul Test:

if __name__ == '__main__':

    room = Roombase ()
    codedir = room.PATH
    # "c:\Users\Gunther\OneDrive\Programmierung\clubdmx_code\dmx"
    head, tail = os.path.split (codedir)
    # head = "c:\Users\Gunther\OneDrive\Programmierung\clubdmx_code"
    head, tail = os.path.split (head)
    # head = "c:\Users\Gunther\OneDrive\Programmierung"

    datadir = os.path.join (head, "clubdmx_rooms")
    print (f"Datadir: {datadir}")

    infotxt = """
---- Roombase Class Test -----
Kommandos: x = Exit
           # = zeige diese Info 
           1 = Raumpfad zeigen
           2 = Neuen Raum '_neu' in c:\\temp
           3 = 'test2' umbenennen
           4 = 'test2' leeren
           5 = 'test2' kopieren
           6 = Raum wechseln
           7 = Raum löschen
           8 = Backup: wohnzimmer -> c:\\temp\\backup
           9 = Restore: c:\\temp\\backup -> test2
           10 = USB backup auf E:
           11 = Neuen Raum auf USB
           12 = USB-Restore jazzitbar nach test2
"""

    print (infotxt)
    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
    
            elif i == '1':
                print (f"Codepfad: {room.codepath}")
                print ( f"Raum: {room.path()}")
                print (f"Raumname: {room.name()}")

            elif i == '2':
                # newpath = room.PATH
                newpath = "c:\\temp\\_neu"
                ret = room.new_room (newpath)
                print (ret["message"], ret["category"])

            elif i == '3':
                newpath = datadir + os.sep + "test2"
                newproj3 = Roombase (newpath)
                newname = input ("Neuer Name für Raum 'test2': ")
                ret = newproj3.rename (newname)
                print (ret["message"], ret["category"])

            elif i == '4':
                newpath = datadir + os.sep + "test2"
                newproj4 = Roombase (newpath)
                ret = newproj4.empty ()
                print (ret["message"], ret["category"])

            elif i == '5':
                oldpath = datadir + os.sep + "test2"
                room = Roombase (oldpath)
                newname = input ("Neuer Name für Raum: ")
                newpath = os.path.join (datadir, newname)
                ret = room.backup (newpath)
                print (ret["message"], ret["category"])

            elif i == '6':
                newpath = input ("In Raum wechseln: ")
                newproj = os.path.join (datadir, newpath)
                ret = room.set_path (newproj)
                print (ret["message"], ret["category"])

            elif i == '7':
                newpath = input ("Raum löschen: ")
                newproj = os.path.join (datadir, newpath)
                ret = room.remove (newproj)
                print (ret["message"], ret["category"])

            elif i == '8':
                newpath = "c:\\temp\\backup"
                roompath = os.path.join (datadir, "wohnzimmer")
                room2 = Roombase (roompath)
                ret = room2.backup (newpath)
                print ("Raum:", roompath)
                print (ret["message"], ret["category"])

            elif i == '9':
                src = "c:\\temp\\backup"
                roompath = os.path.join (datadir, "test2")
                room2 = Roombase (roompath)
                ret = room2.restore (src)
                print ("Raum:", roompath)
                print (ret["message"], ret["category"])

            elif i == '10':
                devices = mount.mnt.list_media_devices()
                print ("USB:", devices)
                if len(devices):
                    ret = room.usbbackup (devices[0])
                else:
                    ret = "kein USB-Laufwerk gefunden."
                print (ret)

            elif i == '11':
                devices = mount.mnt.list_media_devices()
                print ("USB:", devices)
                if len(devices):
                    ret = room.usbbackup (devices[0], neu=True)
                else:
                    ret = "kein USB-Laufwerk gefunden."
                print (ret)

            elif i == '12':
                devices = mount.mnt.list_media_devices()
                print ("USB:", devices)
                if len(devices):
                    roompath = os.path.join (datadir, "test2")
                    room2 = Roombase (roompath)

                    ret = room2.usbrestore (devices[0], "jazzitbar")
                else:
                    ret = "kein USB-Laufwerk gefunden."
                print (ret)
                
            else:
                pass
    finally:
        print ("exit...")
    
