#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" send OSC String """

import argparse
from pythonosc import osc_message_builder
from pythonosc import udp_client

# -------------------------------------------------------------------------
# Modul Test:

if __name__ == '__main__':

    parser = argparse.ArgumentParser (description="Sende einen OSC String")
    parser.add_argument("--ip", help="IP des OSC-Servers")
    parser.add_argument("--port", type=int, help="Port des Servers")
    parser.add_argument ("--address", help="Der Adress-String beginnt mit '/'")
    parser.add_argument ("--value", help="Der zu sendende Wert")
    args = parser.parse_args()

    # Default-Werte setzen:
    if args.ip:
        osc_ip = args.ip
    else:
        osc_ip = "127.0.0.1"

    if args.port:
        osc_port = args.port
    else:
        osc_port = 8800 # Default-Wert in ClubDMX App

    if args.address:
        address = args.address
    else:
        address = "/test"

    if args.value:
        value = args.value
    else:
        value = ""

    client = udp_client.UDPClient(osc_ip, osc_port)
    msg = osc_message_builder.OscMessageBuilder(address = address)
    msg.add_arg (value)
    msg = msg.build()
    client.send (msg)


# class Config:
#     """ Konfiguration von riggingtool mit shelve lesen und speichern,
# Kommandozeile auserten. Wenn Kommandozeilenparameter IP und/oder PORT, dann
# sind diese oberste Priorität"""
#     def __init__(self):
# # Kommandozeilenparameter auswerten:
#         self.commandline = False
#         self.touchipchanged = False
#         self.singlemode = False
#         self.touch_ip = [0 for i in range (TOUCHDEVICES)] #
#         self.universes = 1
        
#         self.parser = argparse.ArgumentParser (description="OSC Fernbedienung für OLA")
#         self.parser.add_argument("--ip", help="IP des ersten Touch-Gerätes")
#         self.parser.add_argument("--port",
#                                  type=int, help="Out-Port der Touch-Geräte")
#         self.parser.add_argument("-c", "--commandline",
#                                  help="Nur Kommandozeilen Optionen, keine Keyboard-Eingabe",
#                                  action="store_true")
#         self.args = self.parser.parse_args()
#         if self.args.commandline:
#             self.commandline = True
        
# # Configfile lesen und auswerten:        
#         self.conffile = sys.argv[0][ : -3]
#         config = shelve.open(self.conffile)
#         if "ola_ip" in config:    # Gerät mit OLA
#             self.ola_ip = config["ola_ip"]
#         else:
#             self.ola_ip = "127.0.0.1"
#             config["ola_ip"] = self.ola_ip
# # OSC-Gerät:            
#         if self.args.ip:
#             self.touch_ip[0] = self.args.ip
#             config["touch_ip"] = self.touch_ip
#         elif "touch_ip" in config:  # Gerät mit Touch-OSC
#             self.touch_ip = config["touch_ip"]
#         else:
#             if self.commandline:
#                 self.touch_ip[0] = "192.168.0.99" # Defaultwert
#             else:
#                 self.touch_ip[0] = input ("IP des ersten Touch-Gerätes: ")
#             config["touch_ip"] = self.touch_ip
# # osc-server hört hier, OLA und touch senden hier            
#         if self.args.port:
#             self.in_port = self.args.port
#             config["in_port"] = self.in_port
#         elif "in_port" in config:   
#             self.in_port = config["in_port"]
#         else:
#             self.in_port = 8000
#             config["in_port"] = self.in_port
# # dieses Programm sendet hier, OLA und touch hören hier            
# # (siehe ola-osc.conf, die Zeile mit udp_listen_port)  
#         if "out_port" in config:  
#             self.out_port = config["out_port"]
#         else:
#             self.out_port = 7770
#             config["out_port"] = self.out_port
# # multi-mode oder single-mode:        
#         if "singlemode" in config:    # Gerät mit OLA
#             self.singlemode = config["singlemode"]
#         else:
#             self.singlemode = 0
#             config["singlemode"] = self.singlemode
# # Anzahl der Universen:
#         if "universes" in config:
#             self.universes = config["universes"]
#         else:
#             self.universes = 1
#             config["universes"] = self.universes

#         config.close ()

