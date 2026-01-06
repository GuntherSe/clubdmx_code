#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Patching:
- Patchliste einlesen
- Prüfen, ob Head-Definitionen vorhanden sind
- Head-Dictionary anlegen
- Dictionary der virtuellen Heads anlegen

TODO:
- _check_headfiles: Behandeln von nicht vorhandenen Headfiles
    - in pdict ein neues Feld ('valid') mit defaultwert False
    - wenn headfile gefunden, dann valid = True
    - Alle weiteren Aktionen davon abhängig machen
- in add_head überlegen, ob hdict und vdict erweitert werden müssen
- in add_head DMX prüfung

"""

import os
import os.path
import csv

from mix import Mix
from csvfileclass import Csvfile
from sort import natural_keys

class Patch (Mix):
    # statische Attribute:
    _init_done = False
    PATCHPATH = ""
    HEADPATH  = ""

    def __init__(self, filename="_neu"):
        if not Patch._init_done:
            Mix.__init__(self)
            self.set_universes (1)
            self.pdict = {}  # Dict der in Patch gefundenen Heads, PatchDict
            self._pfields = [] # type: ignore # Liste der Patch-Attribute
            self.vdict = {}  # Dict der virtuellen Heads, VirtualDict
            self.hdict = {}  # Dict der Attribute der verwendeten Heads, HeadDict
            # Path ermitteln:
            path = os.path.dirname(os.path.realpath(__file__))
            Patch.PATCHPATH = os.path.join (path, "patch") 
            Patch.HEADPATH  = os.path.join (path, "head" )
            fname = os.path.join (Patch.PATCHPATH, filename)
            self.file   = Csvfile (fname)   # Default Patch File Name

            self._get_dictionaries()

# Pfad ändern:
    def set_path (self, newpath):
        """ Pfad ändern """
        Patch.PATCHPATH = os.path.join (newpath, "patch") 
        Patch.HEADPATH  = os.path.join (newpath, "head" )
        self.reload ()

# Dict Methoden: --------------------------------------------------------------
    def _get_dictionaries (self):
        """ pdict, hdict und vdict einlesen

        return: True bei Erfolg, sonst False """
        
        self._get_pdict()

        self._get_hdict()
        self._get_vdict()
        Patch._init_done = True

        if self._check_headfiles():
            # alle Headfiles vorhanden            
            return True
        else:
            print ("Nicht vollständig: Headfiles")
            return False

    def reload (self):
        """ Dict neu laden """
        self._get_dictionaries()
        unis = self.get_unis ()
        if unis:
            self.set_unis (unis)
        
    def _get_pdict (self):
        """ Patchfile einlesen und in PatchDict eintragen

        Struktur: {HeadIndex : ['HeadNr', 'HeadType', 'Addr',
                            'Name', 'Gel', 'Comment'], ...}
        """
        self.pdict = {}  # Dict der in Patch gefundenen Heads, PatchDict
        filename = self.file.name()
        if not os.path.isfile (filename): # Default _pfields
            filename = os.path.join (Patch.PATCHPATH, "_neu")+ os.extsep + "csv"
            with open (filename, 'r',encoding='utf-8',newline='') as pf:
                # zum Lesen öffnen und einlesen
                reader = csv.DictReader (pf, restval= '')
                self._pfields = reader.fieldnames
                # self.pdict bleibt leer
                
        else: # filename gefunden
            with open (filename, 'r',encoding='utf-8',newline='') as pf:
                # zum Lesen öffnen und einlesen
                reader = csv.DictReader (pf, restval= '')
                self._pfields = reader.fieldnames
                count = 0
                for row in reader:
                    attribs = [] # zugehörige Attribute
                    for item in self._pfields: # type: ignore
                        attribs.append (row[item])
                    self.pdict[count] = attribs
                    count += 1

    def _check_headfiles (self):
        """ Prüfen, ob alle Headfiles vorhanden sind
        """
        ret = True
        
        for val in self.pdict.values():
            if self._pfields is None:
                return False
            hindex = self._pfields.index("HeadType") # type: ignore
            hdtype = val[hindex] # HeadType

            if hdtype:
                fname = os.path.join(Patch.HEADPATH, hdtype)
                head = Csvfile (fname)
                check = head.name()
                if not os.path.isfile (check):
                    print ("Head File nicht vorhanden: ", check)
                    ret = False
            else: # hdtype = leer
                print ("Head File Name nicht vorhanden")
                    
        return ret
##TODO: leeres Headfile generieren oder Fehlen anders abfangen

    def pfields (self):
        """ Zeige Liste der in Patch definierten Felder

        Struktur: ['HeadNr', 'HeadType', 'Addr', 'Name', 'Gel', 'Comment']
        """
        return self._pfields


    def patch_line (self, key) ->dict:
        """ Zeile 'key' aus pdict 
        """
        ret = {}
        if key in self.pdict.keys () and self._pfields is not None:
            for i in range (len (self._pfields)):
                ret[self._pfields[i]] = self.pdict[key][i]
        return ret


    def get_unis (self):
        """ configure Mix according to Universes in patch
        """
        ret = []
        if self._pfields is None or "Addr" not in self._pfields:
            print ("Feld 'Addr' nicht vorhanden")
            return ret
        
        aindex = int (self._pfields.index("Addr")) # type: ignore
        for k, v in self.pdict.items ():
            address = v[aindex]
            uni, dmx = address.split (sep='-')
            i = int (uni)
            if i not in ret:
                ret.append (i)
        return ret
    

    def set_unis (self, unilist:list):
        """ configure unis according to patch 
        """
        num = len (unilist)
        if num:
            self.set_universes (num)
            for idx, item in enumerate (unilist):
                self.set_ola_uni (1+idx, item)
        else: #default
            self.set_universes (1)
            self.set_ola_uni (1, 1)


    def headlist (self) -> list:
        """ Liste aller Heads """
        pfields = self._pfields
        if pfields is None or "HeadNr" not in pfields:
            return []
        if pfields is not None:
            index = int (pfields.index("HeadNr"))
        else:
            return []
        hlist = []
        for cnt in self.pdict:
            hlist.append (self.pdict[cnt][index])
        hlist = set (hlist)
        sortlist = sorted (hlist, key=natural_keys)
        return sortlist


    def get_headindex (self, headnr:str) ->list:
        """ einen oder mehrere Indizes zu 'headnr' finden """
        pfields = self._pfields
        if pfields is None:
            return []
        index = int (pfields.index("HeadNr"))
        found = False
        ilist = []
        for cnt in self.pdict:
            if self.pdict[cnt][index] == headnr:
                found = True
                ilist.append (cnt)
        if found:
            return ilist
        else:
            return []
    

    def headdetails (self, headnr:str) -> list:
        """ Attribute aller Heads mit HeadNr headnr

        return: Liste von Dicts (=Dictlist)
        """
        ilist = self.get_headindex (headnr)
        ret = []
        if ilist:
            for item in ilist:
                line = {}
                for i in range (len (self._pfields)): # type: ignore
                    line[self._pfields[i]] = self.pdict[item][i] # type: ignore
                ret.append (line)
        return ret
        

    def attriblist (self, headnr:str) ->list:
        """ Zeige Attribut-Liste eines Head

        Unterschiedlich je nach Head
        Struktur z.B. Dimmer: ['Intensity']
        oder LEDrgb_v: ['Intensity', 'Red', 'Green', 'Blue']
        nur erster gefundener Head wird berücksichtigt.
        Achtung: Heads mit gleicher Headnr müssen gleiche HeadType haben
        """
        hindex = int (self._pfields.index("HeadType")) # type: ignore
        heads = self.get_headindex (headnr)
        if heads:
            head = heads[0] # nur erste Headnr berücksichtigt.
            # found = True
            hdtype = self.pdict[head][hindex] # HeadType
            hfields = list (self.hdict[hdtype].keys())
            #print (hfields)
            hfields.remove ('fieldnames')
            return hfields
        else:
            return []


    def headinfo (self, key:int) ->dict:
        """ Head-Info aus csv Dateien einlesen

        Liefert Dict der Attribute eines Heads, Unterschiedlich je nach Head
        Struktur z.B. Dimmer: {'Intensity': ['0', 'HTP', '0', '255']}
        """
        hindex = int (self._pfields.index("HeadType")) # type: ignore
        
        # geändert: headnr != key
        if key in self.pdict.keys():
            attribdict = {}
            hdtype = self.pdict[key][hindex] # HeadType
            # print ("hdtype: ", hdtype)

            if hdtype:
                head = Csvfile (os.path.join(Patch.HEADPATH, hdtype))
                fname = head.name()
            else:   # = leeres Feld
                return {}
            
            if os.path.isfile (fname):
                with open (fname, 'r',encoding='utf-8',newline='') as headfile:
                    reader = csv.DictReader (headfile)
                    if reader.fieldnames is not None:
                        hfields = list (reader.fieldnames) # Kopie von fieldnames
                        hfields.remove ("Attrib")
                    else:
                        return {}
#                    print (hfields)
                    attribdict["fieldnames"] = hfields
                    for row in reader:
                        attribs = [] # zugehörige Attribute
                        for item in hfields:
                            attribs.append (row[item])
                        attribdict[row["Attrib"]] = attribs
#                print (attribdict)
            return attribdict
        return {}


    def _get_hdict (self):
        """ Head Dictionary einlesen

        Struktur: {'Dimmer': {'Intensity': ['0', 'HTP', '0', '255']}, ... }
        """
        self.hdict = {}
        pfields = self._pfields
        if pfields is None:
            return
        hindex = pfields.index("HeadType")
        for key in self.pdict.keys():
            if not self.pdict[key][hindex] in self.hdict.keys():
#                print ("neu: {}".format (self.pdict[key][hindex]))
                self.hdict[self.pdict[key][hindex]] = self.headinfo (key)
#            else:
#                print ("vorhanden: {}".format (self.pdict[key][0]))

    def _get_vdict (self):
        """ self.vdict für Heads mit virtuellem Dimmer anlegen

        Struktur: {HeadNr: {Intensity: Wert, V-Attrib1: Wert, ...}, ...}
        """
        self.vdict = {}  # Dict der virtuellen Heads, VirtualDict

        pfields = self._pfields
        if pfields is None:
            return
        hindex = pfields.index("HeadType")
        for pkey in self.pdict.keys(): # alle Heads prüfen
            hdtype = self.pdict [pkey][hindex] # Head Type
            #print (hdtype)
            try:                        # Key "Intensity" vorhanden?
                intens = self.hdict[hdtype]["Intensity"]
                if intens[0] == "v":         # virtueller Dimmer
                    self.vdict[pkey] = {} # Dict anlegen
                    self.vdict[pkey]["Intensity"] = intens[2] # Defaultwert
                    # alle anderen Attribute prüfen:
                    for attrib in self.hdict[hdtype].keys():
                        if self.hdict[hdtype][attrib][1] == "vLTP":
                            self.vdict[pkey][attrib] = int(self.hdict[hdtype][attrib][2])
#                print (self.vdict[pkey])
            except KeyError:
                pass
#                print ("Intensity nicht vorhanden")

# File Methoden: --------------------------------------------------------------
        
    def open (self, fname:str) -> dict:
        """ fname öffnen,
        entsprechende Dict-Methoden anwenden,
        """
        ret = {"category":"danger"}
        csvfile = Csvfile (os.path.join(Patch.PATCHPATH, fname))
        openname = csvfile.name ()
        if os.path.isfile (openname):
            current = self.file.name ()
            self.file.name (openname)
            check = self._get_dictionaries()        # True bei Erfolg, sonst False
            if check: 
                unis = self.get_unis ()
                if len (unis):
                    self.set_unis (unis)
                ret["message"] = f"Patch '{fname}' geöffnet."
                ret["category"] = "success"
            else:
                self.file.name (current)
                self._get_dictionaries ()
                ret["message"] = f"Fehler in Headfiles?"
            return ret
        ret["message"] = f"File '{fname}' nicht gefunden."
        return ret
        
    def save (self, newname=None):
        """ Patch Änderungen in Änderungsdatei speichern

        Änderungen in 'Patchfile'.ccsv oder 'newname'.csv speichern
        """

        if newname == None:
            self.file.backup()
            savename = os.path.join(Patch.PATCHPATH, self.file.name ())
        else:
            savename = os.path.join(Patch.PATCHPATH, newname) +os.extsep+"csv"
            
        # print ("Savename: ", savename)
        with open (savename, 'w', newline='',encoding='utf-8') as pf:
            writer = csv.writer(pf) #, quoting=csv.QUOTE_ALL)
# Header schreiben:
            writer.writerow (self._pfields) # type: ignore

# self.pdict schreiben
            # print (self.pdict.keys())
            for num in self.pdict.keys():
                fields = len(self.pdict[num])
                row = [] # , self.pdict[num]]
                for k in range(fields):
                    row.append (self.pdict[num][k])
                writer.writerow (row)
                # print (row)
                
    def dir (self, path=None):
        """ Patch Dir als Liste ausgeben
        """
        if (path == "head"):
            return os.listdir (Patch.HEADPATH)
        else:    
            return os.listdir (Patch.PATCHPATH)
        
# Head Methoden: -------------------------------------------------------------

    def add_head (self):
        """ einen neuen Head einfügen
        HeadNr ist 1 + max(pdict.keys())
        """
        hindex = self._pfields.index("HeadType") # type: ignore
        if self.pdict: # kein leeres pdict
            maxi = max(self.pdict.keys()) + 1
        else:
            maxi = 0
        num = len (self._pfields) # type: ignore

        params = []
        for i in range (num):
            arg = input ("{}: ".format (self._pfields[i])) # type: ignore
            params.append (arg)
#        print (params)
# auf Konsistenz prüfen:
        head = Csvfile (os.path.join(Patch.HEADPATH, params[hindex]))
        fname = head.name()
        
        if not os.path.isfile (fname):
            print ("Head File nicht vorhanden: {}".format (fname))
            return -1
##TODO: DMX Prüfung?      

        self.pdict[maxi] = params
        return maxi

    def remove_head (self, hindex:int) ->None:
        """ Head entfernen
        hindex = HeadIndex (nicht: HeadNr)
        """
        if isinstance(hindex, str):
            hindex = int(hindex)
            
        if hindex in self.pdict.keys():
            self.pdict.pop (hindex)
        if hindex in self.vdict.keys():
            self.vdict.pop (hindex)

# Attribut-Methoden --------------------------------------------------------

    def set_attribute (self, headnr, attrib, value):
        """ Wert des Attribute setzen
        Spezialfall:  virtueller Dimmer
        """
        if isinstance(value, str):
            value = int(value)
        # geändert: headnr != key
        heads = self.get_headindex (headnr)
        if heads:
            for hindex in heads: # alle heads mit HeadNr 'headnr'
                if hindex in self.pdict.keys():
                    tindex  = self._pfields.index("HeadType")  # type: ignore #TypeIndex
                    aindex  = self._pfields.index("Addr")      # type: ignore #AddrIndex
                    hdtype = self.pdict[hindex][tindex]         # z.B. "Dimmer"
                    try:
                        row = self.hdict[hdtype] # Head Infos
                    except KeyError: # beim Raumwechsel, verursacht durch contrib.mix_function()
                        return
                    if attrib in row:
                        # Universum, Adresse:
                        address = self.pdict[hindex][aindex]
                        uni,dmx = address.split(sep='-')
                        uni     = int (uni)
                        dmx     = int (dmx)

                        # Attribut-Size (1, 8 oder 16):
                        if "Size" in row["fieldnames"]:
                            sizeindex = row["fieldnames"].index ("Size")
                            attsize = row[attrib][sizeindex]
                            if attsize == "1":
                                if value < 128:
                                    value = 0
                                else:
                                    value = 255

                        try:
                            vint = row["Intensity"][0]
                        except KeyError: # "Intensity" nicht in Head-Definition
        #                    print ("KeyError?")
                            vint = '0'
                            
                        if vint == 'v': # virtueller Dimmer
                            self.vdict[hindex][attrib] = value # in vdict eintragen
                            if attrib == "Intensity":  # die anderen Attrib anpassen
                                vrow = self.vdict[hindex]
                                for key in vrow.keys():
                                    if not key == "Intensity":
                                        offset = int (row[key][0]) # selber key in hdict
                                        mixval = int ((vrow[key] *value) / 255)
                                        self.set_mixval (uni, dmx+offset, mixval)
                                            
                            else: # Attribut mit virtueller Intensity
                                vintensity = int (self.vdict[hindex]["Intensity"])
                                mixval = int ((vintensity * value) / 255)
                                offset  = int(row [attrib][0])
                                self.set_mixval (uni, dmx+offset, mixval)
                        else:
                            offset  = int(row [attrib][0])
                            self.set_mixval (uni, dmx+offset, value)


    def attribute (self, headnr:str, attrib:str) -> int:
        """ Liefert Attributwert von Head

        Spezial: Virtuelle Attribute
        return: Byte
        """
        heads = self.get_headindex (headnr)
        if heads:
            hindex = heads[0]
        else:
            hindex = None
        
        # geändert: headnr != key

        if hindex in self.pdict.keys():
            tindex = self._pfields.index("HeadType")  # type: ignore # TypeIndex
            hdtype = self.pdict[hindex][tindex]        # HeadType z.B. "Dimmer"
            aindex = self._pfields.index("Addr")      # type: ignore # AddrIndex
            address = self.pdict[hindex][aindex] 
            uni,headdmx = address.split(sep='-')
            uni         = int (uni)
            headdmx     = int (headdmx)
            row = self.hdict[hdtype]
            fn = row["fieldnames"] # fieldnames im Headfile
            if attrib in row:
                #Kriterien für virtuelle Attrib: 'Intensity' == 'v'
                # oder 'Type' == 'vLTP'
                attr = row[attrib][fn.index("Addr")]
                if attr == 'v': # attrib = 'Intensity'
                    return self.vdict[hindex][attrib]
                else:
                    attype = row[attrib][fn.index("Type")]
                    if attype == 'vLTP':
                        return self.vdict[hindex][attrib]
                    else:
                        offset = int(attr)
                        return (self.mixval (uni, headdmx+offset ))
        return 0
                    
    def attribtype (self, headnr:str, attrib:str) ->str:
        """ liefert Attributtyp: 'HTP' oder 'LTP'
        """
        heads = self.get_headindex (headnr)
        if heads:
            hindex = heads[0]
        else:
            hindex = None

        if hindex in self.pdict.keys():
            tindex = int (self._pfields.index("HeadType")) # type: ignore
            hdtype = self.pdict[hindex][tindex] # z.B. "Dimmer"
            # print ("patch-hdtype: ", hdtype)
            row = self.hdict[hdtype]
            fn = row["fieldnames"] # fieldnames im Headfile
            try:
                attype = row[attrib][fn.index("Type")]
                return attype # HTP, LTP, vLTP
            except KeyError:
                return ""
        else:
            return ""
                 

    def color (self, headnr:str) ->list:
        """ Farbwerte des Head in aktuellem Mix

        Intensity: Bei virtuellem Dimmer der Intensity-Wert, bei RGB-Heads ohne
        virtuellem Dimmer = max (Red, Blue, Green), 0 <= Intensity <= 100
        """        
        rgbcolor = [100,255,255,255] # Intensity, Red, Green, Blue
        heads = self.get_headindex (headnr)
        if heads:
            hindex = heads[0]
        else:
            hindex = None
        attriblist = self.attriblist (headnr)
        if hindex in self.pdict.keys():
            if "Red" in attriblist:
                rgbcolor[1] = self.attribute (headnr, "Red")
            if "Green" in attriblist:
                rgbcolor[2] = self.attribute (headnr, "Green")
            if "Blue" in attriblist:
                rgbcolor[3] = self.attribute (headnr, "Blue")
            if "Amber" in attriblist:
                attlevel = int (self.attribute (headnr, "Amber"))
                rgbcolor[1] = max (rgbcolor[1], attlevel)
                rgbcolor[2] = max (rgbcolor[2], int(attlevel * 0.75))
            if "White" in attriblist:
                attlevel = int (self.attribute (headnr, "White") * 0.8)
                rgbcolor[1] = max (rgbcolor[1], attlevel)
                rgbcolor[2] = max (rgbcolor[2], attlevel)
                rgbcolor[3] = max (rgbcolor[3], attlevel)
                
        
            # Head-Typ == virtual Dimmer, RGB-LED oder anderes?
            if "Red" in attriblist:
                mixtype = self.attribtype (headnr, "Red")
                if mixtype == "vLTP":
                    level = int (self.attribute (headnr, "Intensity"))
                else:
                    level = max (rgbcolor[1], rgbcolor[2], rgbcolor[3])
            else: # kein LED - dann level == Wert des ersten Attributs
                level = self.attribute (headnr, attriblist[0])

            # rgbcolor[0] = f"{int(level/2.55)}%"
            rgbcolor[0] = level
               
        return rgbcolor


    def defaults (self, headnr:str) ->list:
        """ set default value for headnr
        """
        ret = []
        hddetails = self.headdetails (headnr)
        hdtype = hddetails[0]["HeadType"]
        dindex = self.hdict[hdtype]["fieldnames"].index ("Default")
        for att in self.attriblist (headnr):
        #    ret[att] = self.hdict[hdtype][att][dindex]
            ret.append ([headnr, att, self.hdict[hdtype][att][dindex]])
        return ret