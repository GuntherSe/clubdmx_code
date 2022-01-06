#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" MIDI Devices 

Hier definiert: Korg NanoKontrol 1 und 2
"""

NO_MIDI_DEVICE = "kein MIDI"

default_buttons = [i for i in range (64)]
default_faders =  [i+64 for i in range (64)]

# Controller-Werte von NanoKONTROL:
Kontrol_faders = [# mode 1, sliders
  2,3,4,5,6,8,9,12,13, 
  # mode 1, knobs
  14,15,16,17,18,19,20,21,22
]
Kontrol_buttons = [
  # up, down
  23, 33, 24, 34, 25, 35, 26, 36, 27, 37, 28, 38, 29, 39, 30, 40, 31, 41,
  # rew, play, ff, repeat, stop, rec
  47, 45, 48, 49, 46, 44
]


# nanoKONTROL2:
Kontrol2_faders = [
  # sliders
  0,1,2,3,4,5,6,7,
  # knobs
  16,17,18,19,20,21,22,23
]

Kontrol2_buttons = [
  # S=solo, M=mute, R=record
  32,48,64, 33,49,65, 34,50,66, 35,51,67, 36,52,68, 37,53,69, 38,54,70, 39,55,71, 
  # rew, ff, stop, play, rec, cycle, 
  43, 44, 42, 41, 45, 46,
  # track back, track fw, marker set, marker back, marker fw
  58, 59, 60, 61, 62
]


midi_device_dict = {"nanoKONTROL": [Kontrol_faders, Kontrol_buttons],
                    "nanoKONTROL MIDI 1": [Kontrol_faders, Kontrol_buttons],
                    "nanoKONTROL2": [Kontrol2_faders, Kontrol2_buttons]}

