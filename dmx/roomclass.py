#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import shutil # fürs kopieren
import tempfile
import csv
from csvnameclass import Csvname
from csvfileclass import dict_to_list

from roombaseclass import Roombase
from csvfileclass import Csvfile

# Liste aller Files in einem Directory:
# siehe: https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
def listfiles (spath:str) -> list:
    return [f for f in os.listdir (spath) \
        if os.path.isfile (os.path.join (spath, f))]

class Room (Roombase):
    """ Die erweiterte Raum-Klasse """
    def __init__ (self, newpath=None):
        Roombase.__init__ (self, newpath)
        self.check_fields ()
        

    def used_cues (self) -> list:
        """ in diesem Raum benutzte Cues als Liste """
        ret = []
        cuepath = self.cuepath()
        ret.append (os.path.join (cuepath, "_neu"))
        for key in self.layout.keys ():
            layline = self.layout.line(key)
            if  layline["Fieldtype"] == "file" and layline["Option"] == "cue":
                # print (f"Key:  {key}, Line: {layline}" )
                searchpath = os.path.join (self.path(), layline["Subdir"])
                filelist = os.listdir (searchpath)
                # print (filelist)
                for item in filelist:
                    fullname = os.path.join (searchpath, item)
                    csvfile = Csvfile (fullname)
                    csvlines = csvfile.to_dictlist ()
                    for l in csvlines:
                        fname = l[layline["Field"]]
                        root, ext = os.path.splitext (fname)
                        search = os.path.join (cuepath, root)
                        if search not in ret:
                            ret.append (search)
        return sorted (ret, key=lambda x: x.lower())


    def unused_cues (self) -> list:
        """ in diesem Raum nicht benutzte Cues """
        ret = []
        cuepath = self.cuepath()
        usedcues = self.used_cues ()
        filelist = os.listdir (self.cuepath ())
        for item in filelist:
            base, ext = os.path.splitext (item)
            search = os.path.join (cuepath, base)
            if search not in usedcues:
                ret.append (search)
        return sorted (ret, key=lambda x: x.lower())


    def remove_unused_cues (self) -> dict:
        """ nicht benutzte Cues löschen 
        .csv und .ccsv Files Löschen
        return: Message
        """
        ret = {}
        c = Csvfile ()
        unused = self.unused_cues ()
        num_unused = len (unused)
        count = 0
        for item in unused:
            rem = item + c.CHGEXT
            if os.path.isfile (rem):
                # print (rem)
                try:
                    os.remove (rem)
                except:
                    count = count + 1
            rem = item + c.CSVEXT
            if os.path.isfile (rem):
                # print (rem)
                try:
                    os.remove (rem)
                except:
                    count = count + 1
        if not count:
            ret["category"] = "success"
            if num_unused == 1:
                ret["message"]  = "Ein Cue wurde gelöscht."
            else:
                ret["message"]  = f"{num_unused} Cues wurden gelöscht."
        else:
            ret["category"] = "danger"
            ret["message"]  = f"{num_unused-count} Cues wurden gelöscht, \
                {count} Cues nicht gelöscht."
        return ret


    def save_changes (self) ->dict:
        """ alle Änderungen in csv-Dateien sichern 
        return: Message
        """
        ret = {}
        c = Csvfile ()
        count = 0   # Files mit Änderungen
        fail = 0    # sichern nicht ok
        for subdir in self.subdirs:
            curpath = os.path.join (self.path(), subdir)
            filelist = os.listdir (curpath)
            for item in filelist:
                base, ext = os.path.splitext (item)
                if ext == c.CHGEXT: # .ccsv gefunden
                    count = count + 1
                    check = False
                    fullname = os.path.join (curpath, base) # + c.CHGEXT
                    c.name (fullname)
                    check = c.save_changes ()
                    if not check:
                        fail = fail + 1
                    else:
                        self.logger.info (f"Änderungen gesichert: {fullname}")

        if fail:
            ret["category"] = "danger"
            if count-fail == 1:
                message = "1 Änderung wurde gesichert, "
            else:
                message = f"{count-fail} Änderungen wurden gesichert, "
            if fail == 1:
                message.append ("1 Änderung nicht gesichert.")
            else:
                message.append (f"{fail} Änderungen nicht gesichert.")
            ret["message"]  = message
        else:
            ret["category"] = "success"
            if count == 1:
                ret["message"]  = "1 Änderung wurde gesichert."    
            else:
                ret["message"]  = f"{count} Änderungen wurden gesichert."
        return ret


    def discard_changes (self) ->dict:
        """ alle Änderungen in csv-Dateien verwerfen 
        return: Message
        """
        ret = {}
        c = Csvfile ()
        count = 0   # Files mit Änderungen
        fail = 0    # verwerfen nicht ok
        for subdir in self.subdirs:
            curpath = os.path.join (self.path(), subdir)
            filelist = os.listdir (curpath)
            for item in filelist:
                base, ext = os.path.splitext (item)
                if ext == c.CHGEXT: # .ccsv gefunden
                    count = count + 1
                    check = False
                    fullname = os.path.join (curpath, base) # + c.CHGEXT
                    c.name (fullname)
                    check = c.discard_changes ()
                    if not check:
                        fail = fail + 1
                    else:
                        self.logger.info (f"Änderungen verworfen: {fullname}")

        if fail:
            ret["category"] = "danger"
            if count-fail == 1:
                message = "1 Änderung wurde verworfen, "
            else:
                message = f"{count-fail} Änderungen wurden verworfen, "
            if fail == 1:
                message.append ("1 Änderung nicht verworfen.")
            else:
                message.append (f"{fail} Änderungen nicht verworfen.")
            ret["message"]  = message
        else:
            ret["category"] = "success"
            if count == 1:
                ret["message"]  = "1 Änderung wurde verworfen."    
            else:
                ret["message"]  = f"{count} Änderungen wurden verworfen."
        ret["count"] = count
        return ret

    def make_archive (self) -> dict:
        """ erstellt ein ZIP-Archiv 
        Return: Message
        """
        ret = {}
        curdir = os.getcwd ()
        zipname = self.name()
        os.chdir (self.rootpath())
        zipfile = shutil.make_archive (zipname, "zip", self.PATH)
        os.chdir (curdir)
        ret["category"] = "success"
        ret["message"]  = f"{zipfile} wurde erzeugt."    
        ret["zipfile"]  = zipfile
        return ret

    def unpack_archive (self, zipfile:str) -> dict:
        """ entpackt zipfile in self.rootpath() 
        zipfile: voller Pfad 
        zipfile in tempdir entpacken, dann alle csv-Files ins
        Raum-Verzeichnis übertragen. 
        Vorhandene csv-Files: die Archivdateien als ccsv-Files speichern.
        Damit ist ein Rückgängigmachen möglich.
        return: Message
        """
        ret = {}
        curdir = os.getcwd ()
        os.chdir (self.rootpath())
        c = Csvname ()
        found = False

        # Entpacken in aktuellen Pfad:
        final_dir = self.path ()
        self.logger.info (f"entpacken nach {final_dir}...")
        extension = c.CHGEXT

        # # Entpacken in originalen Pfad:
        # # zipdir ermitteln:
        # head, tail = os.path.split (zipfile)
        # name, ending = os.path.splitext (tail)
        # final_dir = os.path.join (self.rootpath(), name) # Ziel = Original-Raum
        # # Ziel existiert bereits?
        # if os.path.isdir (final_dir):
        #     extension = c.CHGEXT
        # else:
        #     newroom = Roombase (final_dir) #init
        #     extension = c.CSVEXT

        with tempfile.TemporaryDirectory(dir=".") as tmpdir:
            shutil.unpack_archive (zipfile, extract_dir=tmpdir)
            for subdir in self.subdirs:
                srcpath = os.path.join (tmpdir, subdir)
                if os.path.isdir (srcpath):
                    dstpath = os.path.join (final_dir, subdir)
                    filelist = os.listdir (srcpath) # kann dirs enthalten
                    for item in filelist:
                        srcfile = os.path.join (srcpath, item)
                        if os.path.isfile (srcfile):
                            base, ext = os.path.splitext (item)
                            if ext.lower() == c.CSVEXT: # .CSV gefunden 
                                dstfile = os.path.join (dstpath, item)
                                if os.path.isfile (dstfile):
                                    dstfile = os.path.join (dstpath, base) + extension
                            else:
                                dstfile = os.path.join (dstpath, item)
                            shutil.copy (srcfile, dstfile)
                            found = True

        os.chdir (curdir)
        self.get_layout_files ()
        self.check_fields ()
        
        if found:
            ret["category"] = "success"
            ret["message"]  = f"{zipfile} wurde entpackt."  
        else:
            ret["category"] = "warning"
            ret["message"]  = f"{zipfile} wurde entpackt, es wurden keine "\
                              + "Dateien gefunden."    
        ret["extract_dir"] = final_dir
        return ret

    def check_csv_line (self, line:dict, subdir:str):
        """ in line prüfen, ob alle Regeln des Layout eingehalten werden

        line: zu prüfende Zeile
        subdir: Verzeichnis, für das die Regeln geprüft werden sollen
        Return: line wird direkt geändert
        """
        linekeys = line.keys ()
        defaults = self.layout.defaults (subdir)
        for key in defaults.keys ():
            if key not in linekeys:
                line[key] = defaults[key]
    

    def check_fields (self):
        """ prüfen, ob in den Tabellen alle Felder existieren.
        
        alle Subdirs und hier alle csv-Dateien prüfen 
        Felder ergänzen oder entfernen
        """
        for subdir in self.subdirs:
            subpath = os.path.join (self.PATH, subdir)
            # os.chdir (subpath)
            newcsv = Csvfile (os.path.join (subpath, "_neu") )
            fieldnames = newcsv.fieldnames () # die müssen enthalten sein
            fnset = set (fieldnames)
            dir_content = listfiles (subpath)
            for fname in dir_content: # alle Files prüfen
                # print (f"File: {fname}")
                # newcontent = []
                curfile = Csvfile (os.path.join (subpath, fname))
                curfields = curfile.fieldnames ()
                # alle Feldnamen enthalten?
                # https://stackoverflow.com/questions/1388818/how-can-i-compare-two-lists-in-python-and-return-matches
                if not fnset.intersection (curfields) == fnset:
                    msg = f"Datenbankfehler in den Feldnamen: {subdir} / {fname}"
                    self.logger.warning (msg)
                    curfile.backup () # ccsv File erzeugen
                    newcontent = []
                    fullname = curfile.name ()
                    cur_content = curfile.to_dictlist ()
                    for line in cur_content: # Defaults ergänzen
                        self.check_csv_line (line, subdir)
                        # content neu:
                        newcontent.append (dict_to_list (line, fieldnames))
                    
                    # print (newcontent)
                    with open (fullname, 'w',encoding='utf-8', newline='') as pf:
                        writer = csv.writer (pf)
                        writer.writerow (fieldnames)
                        writer.writerows (newcontent)
                    self.logger.info ("Datenbankfehler korrigiert.")



# --- Modul Test ----------------------------------------------
if __name__ == "__main__":

    room = Room ()
    root = room.rootpath ()
    # "c:\Users\Gunther\OneDrive\Programmierung\clubdmx_code"
    head, tail = os.path.split (root)
    # head = "c:\Users\Gunther\OneDrive\Programmierung"
    datadir = os.path.join (head, "clubdmx_rooms")
    print (f"Datadir: {datadir}")
    room.set_path (os.path.join (datadir, "develop"))
    clip = {'Filename': 'Wand.csv', 'Level': '0', 'Midifader': '7', 'Midiinput': '1', 'Text': 'Wand'}
    
    infotxt = """
    Kommandos: x = Exit
               # = zeige diese Info
               1 = Raumname
               2 = benutzte cues
               3 = unbenutzte cues
               4 = unbenutzte Cues löschen
               5 = alle Datenbank-Änderungen sichern
               6 = erzeuge ZIP-Archiv
               7 = entpacke ZIP-Archiv
               8 = clip mit Defaults ergänzen
               9 = check_fields
    """
    print (infotxt)
    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
            elif i == '1':
                print ("Bin in Raum {}.".format (room.name()))
            elif i == '2':
                usedcues = room.used_cues ()
                for cue in usedcues:
                    print (cue)
                print (f"{len(usedcues)} Cues in Verwendung.")
            elif i == '3':
                unusedcues = room.unused_cues ()
                for cue in unusedcues:
                    print (cue)
                print (f"{len(unusedcues)} Cues nicht in Verwendung.")
            elif i == '4':
                ret = room.remove_unused_cues ()
                print (ret["message"])
            elif i == '5':
                ret = room.save_changes ()
                print (ret["message"])
            elif i == '6':
                ret = room.make_archive ()
                print (ret["message"])
            elif i == '7':
                zipfile = os.path.join (datadir, "test.zip")
                ret = room.unpack_archive (zipfile)
                print ("{}, extract_dir = {}".format (ret["message"],
                                              ret["extract_dir"]))
            elif i == '8':
                print ("clip: ", clip)
                room.check_csv_line (clip, "cuebutton")
                print ("clip neu: ", clip)
            elif i == '9':
                room.check_fields ()
            else:
                pass
    finally:
        print ("exit...")



