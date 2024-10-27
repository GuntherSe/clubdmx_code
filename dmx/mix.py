#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Mix: Übergeordnete Klasse, die die Mixwerte enthält
"""


class Mix :
    """ class Mix contains Mix values, per universe a list of 512 byte values.
    According to the output of the mix values to OLA, it is possible to use 
    arbitrary Universe numbers. The matching from Mix to Univerese numbers is 
    defined in list _ola_unis.
    For example, if i use OLA Univeerse 3, _ola_unis = [3], and the 
    mix values are located in _mix[0][0], _mix[0][1], etc
    """
    _mix = [] # list of mix values
    _ola_unis = []  # Zuordnung mix - OLA Univesum
                    # default: [1,2, ...]
    _universes = 1
    _init_done = False
    
    def __init__(self):
        if not Mix._init_done:
#            self.__mixing = False
            self.set_universes(1)
            Mix._init_done = True
            

    def set_universes (self, num:int):
        """ Anzahl der Universen setzen
        """
        Mix._universes = num
        Mix._ola_unis.clear ()
        for count in range (num):
            Mix._ola_unis.append (count+1)
        self.reset_mix()


    def set_ola_uni (self, mix:int, olanum:int):
        """ pair mix-count to OLA-count  
        
        mix: count from 1
        olanum: count from 1
        """
        Mix._ola_unis[mix-1] = olanum


    def reset_mix (self):
        """ alle Mixwerte auf 0
        """
        Mix._mix = [0 for i in range (Mix._universes)]
        for uni in range (Mix._universes):  # 512 * config.universes DMX Werte
            Mix._mix[uni]  = [0 for i in range (512)] # in Lp berechnete Werte


    def universes (self) -> int:
        """ liefert Anzahl der Universen
        """
        return Mix._universes
        

    def set_mixval(self, uni:int, chan:int, val:int):
        """ einen mix-Wert setzen

        uni:  count from 1
        chan: count from 1
        val: 0 <= val <= 255
        """
        if isinstance(uni, str):
            uni = int(uni)
        if isinstance(chan, str):
            chan = int(chan)
        if isinstance(val, str):
            val = int(val)
        try:
            mixnum = self._ola_unis.index (uni)
            Mix._mix [mixnum][chan-1] = val
            # Mix._mix [uni-1][chan-1] = val
        except:
            pass

    def set_addrval (self, addr:str, val:int):
        """ Mixwert an Adresse schreiben

        addr = str 'uni-chan'
        uni: count from 1
        val: 0 <= val <= 255
        """
        uni,chan = addr.split(sep='-')
        uni  = int(uni)
        chan = int(chan)
        if isinstance(val, str):
            val = int(val)
        try:
            mixnum = self._ola_unis.index (uni)
            Mix._mix [mixnum][chan-1] = val
            # Mix._mix [uni-1][chan-1] = val
        except:
            pass
        
    def mixval (self, uni:int, chan:int):
        """ Mix-Wert von uni - chan liefern

        uni, chan ab 1
        """
        try:
            mixnum = self._ola_unis.index (uni)
            return Mix._mix [mixnum][chan-1]
            # return Mix._mix[uni-1][chan-1]
        except:
            return 0

    def show_mix (self, uni:int):
        """ mix(uni) anzeigen

        uni: count from 1
        """
        if isinstance(uni, str):
            uni = int(uni)
        try:
            mixnum = self._ola_unis.index (uni)
            return Mix._mix[mixnum]
        except:             # IndexError
            return []

# ------------------------------------------------------------------------------
# Unit Test:        
if __name__ == "__main__":

    mix = Mix ()
    mix.set_universes (2)
    mix.set_ola_uni (1, 5)
    
    infotxt = """
    ---- Lichtpult + OLA -----

    Kommandos: x = Exit
               # = diese Info
               1 = Anzahl der Universen = 1
               2 = Anzahl der Universen = 2
               3 = Test set_mixval
               4 = zeige Uni 2
               5 = zeige Uni 5
               6 = mixval 2-1
               r = Reset Mix
    """
    print (infotxt)
    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
            elif i == '1':
                mix.set_universes (1)
                print (mix.universes())
            elif i == '2':
                mix.set_universes (2)
                print (mix.universes())
            elif i == '3':
                mix.set_mixval (2, 1,255)
                mix.set_addrval ('2-2', 123)
                mix.set_mixval (5,1,50)
                mix.set_mixval (5,2,55)
            elif i == '4':
                print (mix.show_mix (2))
            elif i == '5':
                print (mix.show_mix (5))
            elif i == '6':
                print (mix.mixval (2,1))
            elif i == 'r':
                mix.reset_mix ()
            else:
                pass
    finally:
        print ("exit...")
    
    
