#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" MIDI Devices 

Hier definiert: Korg NanoKontrol 1 und 2

"""

# Konstanten:
MODE_1 = 0
MODE_2 = 1
MODE_3 = 2
MODE_4 = 3

# MAXFADERS = 20  # Maximale Anzahl der Fader
NO_MIDI_DEVICE = "kein MIDI"

default_faders = {i:i for i in range (127)}
default_buttons = [i for i in range (127)]

# Controller-Werte von NanoKONTROL:
Kontrol_faders = [{
  # mode 1, sliders
   2:  0,  3:  1,  4:  2,  5:  3,  6:  4,  8:  5,  9:  6, 12:  7, 13:  8,
  # mode 1, knobs
  14:  9, 15: 10, 16: 11, 17: 12, 18: 13, 19: 14, 20: 15, 21: 16, 22: 17,
  },{
  # mode 2, sliders
  42:  0, 43:  1, 50:  2, 51:  3, 52:  4, 53:  5, 54:  6, 55:  7, 56:  8,
  # mode 2, knobs
  57:  9, 58: 10, 59: 11, 60: 12, 61: 13, 62: 14, 63: 15, 65: 16, 66: 17,
  },{
  # mode 3, sliders
  85:  0, 86:  1, 87:  2, 88:  3, 89:  4, 90:  5, 91:  6, 92:  7, 93:  8,
  # mode 3, knobs
  94:  9, 95: 10, 96: 11, 97: 12, 102: 13, 103: 14, 104: 15, 105: 16, 106: 17,
  },{
  # mode 4, sliders
  7: 0, 263: 1, 519: 2, 775: 3, 1031: 4, 1287: 5, 1543: 6, 1799: 7, 2055: 8,
  # mode 4, knobs
  10: 9, 266: 10, 522: 11, 778: 12, 1034: 13, 1290: 14, 1546: 15, 1802: 16,
  2058: 17,
  }]
Kontrol_buttons = [[
  # mode 1
  # up, down
  23, 33, 24, 34, 25, 35, 26, 36, 27, 37, 28, 38, 29, 39, 30, 40, 31, 41,
  # rew, play, ff, repeat, stop, rec
  47, 45, 48, 49, 46, 44
],[
  # mode 2
  # up, down
  67, 76, 68, 77, 69, 78, 70, 79, 71, 80, 72, 81, 73, 82, 74, 83, 75, 84,
  # rew, play, ff, repeat, stop, rec
  47, 45, 48, 49, 46, 44
],[
  # mode 3
  # up, down
  107, 116, 108, 117, 109, 118, 110, 119, 111, 120, 112, 121, 113, 122, 114, 123, 115, 124,
  # rew, play, ff, repeat, stop, rec
  47, 45, 48, 49, 46, 44
],[
  # mode 4
  # up, down
  16, 17, 272, 273, 528, 529, 784, 785, 1040, 1041, 1296, 1297, 1552, 1553, 1808, 1809, 2064, 2065,
  # rew, play, ff, repeat, stop, rec
  47, 45, 48, 49, 46, 44
]]

# nanoKONTROL2:
Kontrol2_faders = {
  # sliders
   0:  0,  1:  1,  2:  2,  3:  3,  4:  4,  5:  5,  6:  6, 7:  7, 
  # knobs
  16:  8, 17:  9, 18: 10, 19: 11, 20: 12, 21: 13, 22: 14, 23: 15, 
  }
Kontrol2_buttons = [
  # S=solo, M=mute, R=record
  32,48,64, 33,49,65, 34,50,66, 35,51,67, 36,52,68, 37,53,69, 38,54,70, 39,55,71, 
  # rew, ff, stop, play, rec, cycle, 
  43, 44, 42, 41, 45, 46,
  # track back, track fw, marker set, marker back, marker fw
  58, 59, 60, 61, 62
]

midi_device_dict = {"nanoKONTROL": [Kontrol_faders[MODE_1], Kontrol_buttons[MODE_1]],
                    "nanoKONTROL MIDI 1": [Kontrol_faders[MODE_1], Kontrol_buttons[MODE_1]],
                    "nanoKONTROL2": [Kontrol2_faders, Kontrol2_buttons]}

