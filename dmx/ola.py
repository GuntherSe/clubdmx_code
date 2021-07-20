#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Schnittstelle zwischen Lichtpult und OLA
#!/usr/bin/env python3
- Empfangen der aktuellen Werte
- Senden der im Lichtpult errechneten Werte an die jeweiligen Universen

"""

# OLARECEIVESTRING = "/ola/universe/"
OLASENDSTRING    = "/dmx/universe/"

# import math
import socket
import threading
import array
import time
# import urllib.request # um ola plugins neu zu laden mit "localhost:9090/reload"

# from pythonosc import dispatcher
# from pythonosc import osc_server
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
In self.__dmx sind die aktuellen Werte aller Universen eingelesen
In self.__mix sind die im Lichtpult berechneten Werte, die zu senden sind
Vor Verwendung festzulegende Variablen:
ola_ip, out_port, universes, 
"""
    olacount = 0
    
    def __init__(self):
        OscOla.olacount += 1
        # print ("Ola Count", OscOla.olacount)
        
        Mix.__init__(self)
        self.ola_ip = "127.0.0.1"
        self.out_port = 7770

        self.timeout = 0.05 # 0.05
        self.mix_thread = threading.Thread(target=self.run)
        self.mix_thread.setDaemon (True)
        # self.__mixing = False
        self.paused = False
        # self.pause_cond = threading.Condition (threading.Lock ())

        self.client = udp_client.UDPClient(self.ola_ip, self.out_port)
        self.set_universes (1)    

        # self.mix_thread.start ()


    def set_ola_ip (self, newip):
        self.ola_ip = newip
        self.client.__init__ (self.ola_ip, self.out_port)


    def set_out_port (self, newport):
        self.out_port = newport
        self.client.__init__ (self.ola_ip, self.out_port)
        

    def update_uni(self, uni):  # mix-Werte nach Ola senden
        msgaddress = OLASENDSTRING + "{0}".format (uni)
        self.msg = osc_message_builder.OscMessageBuilder(address = msgaddress)
#        arg = array.array('B', self.__mix[uni-1]).tostring()
# Python 3.9 error:
#        arg = array.array('B', self.show_mix(uni)).tostring()
        arg = array.array('B', self.show_mix(uni)).tobytes()
        self.msg.add_arg (arg)
        self.msg = self.msg.build()
        self.client.send (self.msg)

    def run (self): # 
        """ Mix an Ola senden """
        while True:
            for i in range (self.universes()):
                self.update_uni (1+i)
            time.sleep(self.timeout)

    def start_mixing (self):
        """ Mix starten """
        self.mix_thread.start ()
    
        
# ------------------------------------------------------------------------------
# Unit Test:        
if __name__ == "__main__":

    ola   = OscOla ()
    ola.set_ola_ip ("192.168.0.19")
    #ola.set_universes (2)
    print("Verbinde zu OLA-device: {0}".format (ola.ola_ip))

    # dieser Rechner:
    local_ip = get_ip_address()
    print("Meine IP: {}".format(local_ip))

    ola.start_mixing()
    
    print("---- Lichtpult + OLA -----\n")
    print("Kommandos: x = Exit")
    print("           u = Anzahl der Universen")
    print("           r = Reset  der Universen")
    print("           1 = diverse Werte setzen")
    print("           2 = diverse Werte setzen")
    print("           3 = OLA Channel 1-2 lesen")
    print("           4 = Universes = 2")
    print("           5 = diverse Werte auf Uni 2 setzen")
    print("           6 = OLA Channel 2-1 lesen")
    print("           7 =  Uni 1 lesen")
    print("           8 =  Uni 2 lesen")
        
    try:
        i = 1
        while i:
            i = input ("CMD: ")
            if i == 'x': break
            elif i == 'u':
                print (ola.universes())
            elif i == 'r':
                ola.reset_mix()
            elif i == '1':
                ola.set_mixval (1,43, 255)
                ola.set_mixval (1,2, 127)
                ola.set_mixval (1,3, 12)
            elif i == '2':
                ola.set_mixval (1,43, 0)
                ola.set_mixval (1,2, 255)
                ola.set_mixval (1,3, 0)
            elif i == '3':
                print (ola.mixval(1,2))
            elif i == '4':
                ola.set_universes (2)
                #print (ola.show_mix (2))
            elif i == '5':
                ola.set_mixval (2,1, 255)
                ola.set_mixval (2,2, 127)
                ola.set_mixval (2,3, 12)
            elif i == '6':
                print (ola.mixval(2,2))
            elif i == '7':
                print (ola.show_mix(1))
            elif i == '8':
                print (ola.show_mix (2))
                       
            elif i == '':
                i=1
            else:
                pass
    finally:
        print ("bye...")

    
    
