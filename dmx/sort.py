#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://www.tutorialspoint.com/How-to-correctly-sort-a-string-with-a-number-inside-in-Python

import re

def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)',text) ]    


# ------------------------------------------------------------------------------
# Unit Test:        
if __name__ == "__main__":


    import pprint # pretty print
# from operator import itemgetter, attrgetter # zur Sortierung

    pp = pprint.PrettyPrinter(depth=6)

    csvdict = {0: ['1', '1. Stimmun', 'Cue1', ''], 
           1: ['2', '2. Stimmung', 'Cue2', ''], 
           2: ['3', 'Einlaß neu', 'Cue3', ''], 
           3: ['4', 'GL neu und wichtig', 'newcue', ''], 
           4: ['12', 'GL Studio', 'studio_gl', ''], 
           5: ['7', 'sechs', 'Cue3', ''], 
           6: ['6', 'hinten, vorne', 'Cue3', ''], 
           7: ['8', 'acht', '', ''], 
           8: ['9', 'neun', '', ''], 
           9: ['10', 'zehn', '', '']}

    cuedict = {'fieldnames': ['Nummer', 'Text', 'Filename', 'Level'],
        0: ['1', 'rot', 'rot', '0.2275'],
        1: ['3', 'blau', 'blau', '0.0706'],
        2: ['12', 'grün', 'grün', '0.0314']
        }

    dictlist = [
        {'Name': '1abc10', 'Type': 'Head', 'Text': 'Spot 1', 'Left': '20px', 'Top': '40px', 'Width': '120px', 'Height': '90px', 'Comment': 'Kommentar'}, 
        {'Name': 'abc2', 'Type': 'Head', 'Text': 'Spot 2', 'Left': '160px', 'Top': '40px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '3', 'Type': 'Head', 'Text': 'Spot 3', 'Left': '300px', 'Top': '40px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '4', 'Type': 'Head', 'Text': 'Spot 4', 'Left': '440px', 'Top': '40px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '5', 'Type': 'Head', 'Text': 'Spot 5', 'Left': '580px', 'Top': '40px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '6', 'Type': 'Head', 'Text': 'Spot 6', 'Left': '720px', 'Top': '40px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '7', 'Type': 'Head', 'Text': 'Links1', 'Left': '20px', 'Top': '150px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '8', 'Type': 'Head', 'Text': 'Links2', 'Left': '160px', 'Top': '150px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '9', 'Type': 'Head', 'Text': 'Links 3', 'Left': '300px', 'Top': '150px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '10', 'Type': 'Head', 'Text': '10', 'Left': '440px', 'Top': '150px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '11', 'Type': 'Head', 'Text': 'Spot 11', 'Left': '580px', 'Top': '150px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '15', 'Type': 'Head', 'Text': 'Spot 15', 'Left': '300px', 'Top': '260px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '16', 'Type': 'Head', 'Text': 'Spot 16', 'Left': '440px', 'Top': '260px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '17', 'Type': 'Head', 'Text': 'Spot 17', 'Left': '580px', 'Top': '260px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '12', 'Type': 'Head', 'Text': 'Spot 12', 'Left': '720px', 'Top': '150px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '13', 'Type': 'Head', 'Text': 'Spot 13', 'Left': '20px', 'Top': '260px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '14', 'Type': 'Head', 'Text': 'Spot 14', 'Left': '160px', 'Top': '260px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '18', 'Type': 'Head', 'Text': 'Spot 18', 'Left': '720px', 'Top': '260px', 'Width': '120px', 'Height': '90px', 'Comment': ''},
        {'Name': '119', 'Type': 'Head', 'Text': 'FlatPro 1', 'Left': '19.6px', 'Top': '369.6px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '20', 'Type': 'Head', 'Text': 'FlatPro 2', 'Left': '160px', 'Top': '370px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '21', 'Type': 'Head', 'Text': 'FlatPro 3', 'Left': '300px', 'Top': '370px', 'Width': '120px', 'Height': '90px', 'Comment': ''}, 
        {'Name': '22', 'Type': 'Head', 'Text': 'FlatPro 4', 'Left': '560px', 'Top': '368px', 'Width': '120px', 'Height': '90px', 'Comment': ''}
        ]


    infotxt = """
    ---- Test Sortierung -----

    Kommandos: x = Exit
               # = zeige diese Info
               1 = sortiere CSV-Dict
               2 = sortiere Cue-Dict
               3 = sortiere Dict-Liste (Stage)
    """        
    print (infotxt)
    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
            elif i == '1':
                sortlist = sorted (csvdict.items(), key=lambda x: int (x[1][0]))
                print ("sortiertes CSV-Dict:")
                pp.pprint (sortlist)
            elif i == '2':
                sortlist = sorted (cuedict.items(), key=lambda x: natural_keys (x[1][0]))
                print ("sortiertes Cue-Dict:")
                pp.pprint (sortlist)
            elif i == '3':
                sortlist = sorted (dictlist, key=lambda x: natural_keys (x["Name"]))
                print ("sortierte Dict-Liste:")
                for i in range (len (sortlist)):
                    print (sortlist[i])
    finally:
        print ("exit...")
        