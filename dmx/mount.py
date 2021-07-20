#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import shutil

if os.name == "posix":
    import mount_posix as mnt
else:
    # print ("OS = nt")
    import mount_nt as mnt


def get_usbchoices () ->list:
    """ Choice für SelectField in Forms 
    """
    devices = mnt.list_media_devices()
    # num_devices = len (devices)
    choices = []
    for device in devices:
        choices.append ((device, mnt.get_label (device)))
    return choices


if __name__ == "__main__":

    devices = mnt.list_media_devices()
    num_devices = len (devices)
    medianum = 0
    if num_devices:
        pass

    
    infotxt = """
    Kommandos: x = Exit
               # = zeige diese Info
               u = Anzahl der Devices
               1,2,3 = Mediennummer
               t = mkdir 'test'
               r = shutil.rmtree 'test'
               l = Choices-Liste
    """
    print (infotxt)
    try:
        i = 1
        while i != 'x':
            i = input ("CMD: ")
            if i == 'u':
                print ("{} Medienlaufwerke gefunden".format (num_devices))
            elif i == '#':
                print (infotxt)
            elif i == '1':
                medianum = 0
                print ("Verwende {}.".format (devices[medianum]))
            elif i == '2':
                medianum = min (1, num_devices-1)
                print ("Verwende {}.".format (devices[medianum]))
            elif i == '3':
                medianum = min (2, num_devices-1)
                print ("Verwende {}.".format (devices[medianum]))
            elif i == 't':
                if num_devices:
                    dev = devices[medianum]
                    print ("dev: ", dev)
                    mnt.mount (dev)
                    mediapath = mnt.get_media_path (dev)
                    print ("mediapath:", mediapath)
                    testdir = os.path.normpath ( os.path.join (mediapath, "test"))
                    try:
                        os.mkdir (testdir)
                        print ("ok")
                    except FileExistsError:
                        print ("Verzeichnis 'test' ist bereits vorhanden")
                    mnt.unmount (dev)
                else:
                    print ("Kein Medienlaufwerk gefunden.")
            elif i == 'r':
                if num_devices:
                    dev = devices[medianum]
                    mnt.mount (dev)
                    mediapath = mnt.get_media_path (dev)
                    testdir = os.path.normpath ( os.path.join (mediapath, "test"))
                    try:
                        shutil.rmtree (testdir)
                        print ("ok")
                    except:
                        print ("Fehler beim Entfernen von {}".format (testdir))
                    mnt.unmount (dev)
            elif i == 'l':
                print (get_usbchoices ())
            else:
                pass
    finally:
        print ("exit...")



