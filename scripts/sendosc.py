#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" send OSC String """

import argparse
from pythonosc import osc_message_builder
from pythonosc import udp_client

# -------------------------------------------------------------------------

if __name__ == '__main__':

    parser = argparse.ArgumentParser (description="Sende einen OSC String")
    parser.add_argument("-i", "--ip", help="IP des OSC-Servers")
    parser.add_argument("-p", "--port", type=int, help="Port des Servers")
    parser.add_argument ("-a","--address", help="Der Adress-String beginnt mit '/'")
    parser.add_argument ("-e", "--value",nargs='*', help="Die zu sendenden Werte")
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

    print (f"{osc_ip}:{osc_port} {address} {value} ")
    client = udp_client.UDPClient(osc_ip, osc_port)
    msg = osc_message_builder.OscMessageBuilder(address = address)
    msg.add_arg (value)
    msg = msg.build()
    client.send (msg)

