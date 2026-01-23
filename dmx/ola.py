#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Schnittstelle zwischen Lichtpult und OLA
#!/usr/bin/env python3
- Empfangen der aktuellen Werte
- Senden der im Lichtpult errechneten Werte an die jeweiligen Universen

"""

OLASENDSTRING    = "/dmx/universe/"

import socket
import threading
import array
import time

from pythonosc import osc_message_builder
from pythonosc import udp_client

from mix import Mix

# ------------------------------------------------------------------------------
# http://stackoverflow.com/questions/166506/
# finding-local-ip-addresses-using-pythons-stdlib
def get_ip_address():
    return ([(s.connect(('8.8.8.8', 80)),s.getsockname()[0], s.close())
           for s in [socket.socket (socket.AF_INET, socket.SOCK_DGRAM)]][0][1])
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
class OscOla (Mix):
    """ Verbindung zu Ola:

    In self._mix sind die im Lichtpult berechneten Werte, die zu senden sind
    Vor Verwendung festzulegende Variablen:
    ola_ip, out_port, universes, 
    """
    def __init__(self):
        
        self.ola_ip = "127.0.0.1"
        self.out_port = 7770
        Mix.__init__(self)

        self.timeout = 0.04 # 0.05
        self.mix_thread = threading.Thread(target=self.run, daemon=True)
        self.paused = False

        self.client = udp_client.UDPClient(self.ola_ip, self.out_port)


    def set_ola_ip (self, newip):
        self.ola_ip = newip
        self.client.__init__ (self.ola_ip, self.out_port)


    def set_out_port (self, newport):
        self.out_port = newport
        self.client.__init__ (self.ola_ip, self.out_port)


    def update_uni(self, uni): 
        """ mix-Werte nach Ola senden

        uni: zählen ab 1
        """
        msgaddress = OLASENDSTRING + f"{uni}"
        self.msg = osc_message_builder.OscMessageBuilder(address = msgaddress)
        arg = array.array('B', self.show_mix(uni)).tobytes()
        self.msg.add_arg (arg)
        self.msg = self.msg.build()
        self.client.send (self.msg)


    def run (self): # 
        """ Mix an Ola senden """
        while True:
            for uni in self._ola_unis:
                self.update_uni (uni)
            time.sleep(self.timeout)


    def start_mixing (self):
        """ Mix starten """
        self.mix_thread.start ()
    
        
# ------------------------------------------------------------------------------
# Unit Test:        
if __name__ == "__main__":
    import os

    ola   = OscOla ()
    olaip = os.environ.get ("OLAIP", default="127.0.0.1")
    ola.set_ola_ip (olaip)
    #ola.set_universes (2)
    print("Verbinde zu OLA-device: {0}".format (ola.ola_ip))

    # dieser Rechner:
    local_ip = get_ip_address()
    print("Meine IP: {}".format(local_ip))

    ola.start_mixing()
    
    infotxt = """
    ---- Lichtpult + OLA -----

    Kommandos: x = Exit
               # = Zeige diese Info
               u = Anzahl der Universen
               r = Reset  der Universen
               1 = diverse Werte auf Uni 1 setzen
               2 = diverse Werte auf Uni 2 setzen
               3 = OLA Channel 1-2 lesen
               4 = Universes = 2
               5 = diverse Werte auf Uni 5 setzen
               6 = OLA Channel 2-1 lesen
               7 = zeige Uni 1
               8 = zeige Uni 2
               9 = Mix 1 <-> OLA Uni 3
              10 = diverse Werte auf Uni 3 setzen 
              11 = zeige Uni 3
    """

    print (infotxt)        
    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == '#':
                print (infotxt)
            # if i == 'x': break
            elif i == 'u':
                print (ola.universes())
            elif i == 'r':
                ola.reset_mix()
            elif i == '1':
                ola.set_mixval (1,43, 255)
                ola.set_mixval (1,2, 127)
                ola.set_mixval (1,3, 12)
            elif i == '2':
                ola.set_mixval (2,43, 10)
                ola.set_mixval (2,2, 255)
                ola.set_mixval (2,3, 110)
            elif i == '3':
                print (ola.mixval(1,2))
            elif i == '4':
                ola.set_universes (2)
                #print (ola.show_mix (2))
            elif i == '5':
                ola.set_mixval (5,1, 255)
                ola.set_mixval (5,2, 127)
                ola.set_mixval (5,3, 12)
            elif i == '6':
                print (ola.mixval(2,2))
            elif i == '7':
                print (ola.show_mix(1))
            elif i == '8':
                print (ola.show_mix (2))
            elif i == "9":
                print (f"Mix 1 geht an Uni 3")
                ola.set_ola_uni (1,3)
            elif i == '10':
                ola.set_mixval (3,43, 255)
                ola.set_mixval (3,2, 127)
                ola.set_mixval (3,3, 12)
            elif i == '11':
                print (ola.show_mix(3))
                       
            else:
                pass
    finally:
        print ("bye...")

    
    
