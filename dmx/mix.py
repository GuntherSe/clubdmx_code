#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Mix: Übergeordnete Klasse, die die Mixwerte enthält
"""

# import threading
# import time

class Mix :
    # global:
    _mix = []
    _universes = 1
    _init_done = False
    
    def __init__(self):
        if not Mix._init_done:
#            self.__mixing = False
            self.set_universes(1)
            Mix._init_done = True
            
    def set_universes (self, num):
        """ Anzahl der Universen setzen
        """
        Mix._universes = num
        self.reset_mix()

    def reset_mix (self):
        """ alle Mixwerte auf 0
        """
        Mix._mix = [0 for i in range (Mix._universes)]
        for uni in range (Mix._universes):  # 512 * config.universes DMX Werte
            Mix._mix[uni]  = [0 for i in range (512)] # in Lp berechnete Werte

    def universes (self):
        """ liefert Anzahl der Universen
        """
        return Mix._universes
        
    def set_mixval(self, uni, chan, val):
        """ einen mix-Wert setzen
        hat Priorität, dh add_mixval wird überschrieben
        """
        if isinstance(uni, str):
            uni = int(uni)
        if isinstance(chan, str):
            chan = int(chan)
        if isinstance(val, str):
            val = int(val)
        try:
            Mix._mix [uni-1][chan-1] = val
        except:
            pass

    def set_addrval (self, addr, val):
        """ Mixwert an Adresse schreiben
        addr = str 'uni-chan'
        """
        uni,chan = addr.split(sep='-')
        uni  = int(uni)
        chan = int(chan)
        if isinstance(val, str):
            val = int(val)
        try:
            Mix._mix [uni-1][chan-1] = val
        except:
            pass
        
    def mixval (self, uni, chan):
        """ Mix-Wert von uni - chan liefern
        """
        try:
            return Mix._mix[uni-1][chan-1]
        except:
            return

    def show_mix (self, uni):
        """ mix(uni) anzeigen
        """
        if isinstance(uni, str):
            uni = int(uni)
        try:
            return Mix._mix[uni-1]
        except:             # IndexError
            return []

# ------------------------------------------------------------------------------
# Unit Test:        
if __name__ == "__main__":

    mix = Mix ()
    mix.set_universes (2)
    
    print("---- Lichtpult + OLA -----\n")
    print("Kommandos: x = Exit")
    print("           1 = Anzahl der Universen = 1")
    print("           2 = Anzahl der Universen = 2")
    print("           3 = Test set_mixval")
    print("           4 = Show Uni 2")
    print("           5 = Reset Mix")
    print("           6 = mixval 2-1")

    try:
        #i = 1
        while True:
            i = input ("CMD: ")
            if i == 'x': break
            elif i == '1':
                mix.set_universes (1)
                print (mix.universes())
            elif i == '2':
                mix.set_universes (2)
                print (mix.universes())
            elif i == '3':
                mix.set_mixval (2, 1,255)
                mix.set_addrval ('2-2', 123)
            elif i == '4':
                print (mix.show_mix (2))
            elif i == '5':
                mix.reset_mix ()
            elif i == '6':
                print (mix.mixval (2,1))
##            elif i == '':
##                i=1
            else:
                pass
    finally:
        print ("exit...")
    
    
