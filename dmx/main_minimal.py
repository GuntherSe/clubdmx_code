#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Minimal Lichtpult: Test Patch und OlaOsc

"""

# from mix   import Mix
from patch import Patch
from ola   import OscOla

def inputNumber(message, default=0):
    while True:
        try:
           userInput = input(message)
           if userInput == '':
               print ("Default")
               userInput = default
           else:
               userInput = int(userInput)
        except ValueError:
           print("Not an integer! Try again.")
           continue
        else:
           return userInput 
           break 
        

if __name__ == "__main__":

    patch = Patch ()
    ola   = OscOla ()
    ola.set_ola_ip ("192.168.0.19")
    print("Verbinde zu OLA-device: {0}".format (ola.ola_ip))
#    ola.start_server ()
    ola.start_mixing()
    print("---- Lichtpult Minimal Test -----\n")
    print("Kommandos: x = Exit")
    print("           h = Head")
    print("           i = Intensität")
    print("           r = Rot")
    print("           g = Grün")
    print("           b = Blau")
    
    try:
        i = 1
        head = 13
        while i:
            i = input ("CMD: ")
            if i == 'x': break
            elif i == 'h':
                val = inputNumber ("Head: ({}): ".format (head), head)
                head = val
            elif i == 'i':
                val = inputNumber ("Intensität: ")
                patch.set_attribute (head, "Intensity", val)
            elif i == 'r':
                val = inputNumber ("Rot: ")
                patch.set_attribute (head, "Red", val)
            elif i == 'g':
                val = inputNumber ("Grün: ")
                patch.set_attribute (head, "Green", val)
            elif i == 'b':
                val = inputNumber ("Blau: ")
                patch.set_attribute (head, "Blue", val)
            
            else:
                pass
    finally:
#        ola.stop_server()
        # ola.stop_mixing()
        print ("exit...")
