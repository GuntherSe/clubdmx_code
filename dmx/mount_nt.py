#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: GS
#
# Date Created: 30.8.2020
# Last Modified: 
#
# Developed and tested using Python 3.6

import os
import os.path
import wmi
import pythoncom

DRIVE_TYPES = {0 : "Unknown",
    1 : "No Root Directory",
    2 : "Removable Disk",
    3 : "Local Disk",
    4 : "Network Drive",
    5 : "Compact Disc",
    6 : "RAM Disk"
    }


def list_drive_devices () ->list:
    """ alle Laufwerke auflisten 
    Liste aus drive-Objekten
    """
    devices = []
    c = wmi.WMI ()
    for drive in c.Win32_LogicalDisk ():
        devices.append (drive)
    return devices

def drive_properties (devlist) -> "print":
    """ alle Properties ausgeben """
    for device in devlist:
        print ("Availability: ", device.Availability)
        print ("BlockSize: ", device.BlockSize , " Caption: ", device.Caption )
        print ("Compressed: ", device.Compressed , " ConfigManagerErrorCode: ", device.ConfigManagerErrorCode )
        print ("ConfigManagerUserConfig: ", device.ConfigManagerUserConfig , " CreationClassName: ", device.CreationClassName )
        print ("Description: ", device.Description , " DeviceID: ", device.DeviceID )
        print ("DriveType: ", device.DriveType , " ErrorCleared: ", device.ErrorCleared )
        print ("ErrorDescription: ", device.ErrorDescription , " ErrorMethodology: ", device.ErrorMethodology )
        print ("FileSystem: ", device.FileSystem , " FreeSpace: ", device.FreeSpace )
        print ("InstallDate: ", device.InstallDate , " LastErrorCode: ", device.LastErrorCode )
        print ("MaximumComponentLength: ", device.MaximumComponentLength , " MediaType: ", device.MediaType )
        print ("Name: ", device.Name , " NumberOfBlocks: ", device.NumberOfBlocks )
        print ("PNPDeviceID: ", device.PNPDeviceID , " PowerManagementSupported: ", device.PowerManagementSupported )
        print ("ProviderName: ", device.ProviderName , " Purpose: ", device.Purpose )
        print ("QuotasDisabled: ", device.QuotasDisabled , " QuotasIncomplete: ", device.QuotasIncomplete )
        print ("QuotasRebuilding: ", device.QuotasRebuilding , " Size: ", device.Size )
        print ("Status: ", device.Status , " StatusInfo: ", device.StatusInfo )
        print ("SupportsDiskQuotas: ", device.SupportsDiskQuotas , " SupportsFileBasedCompression: ", device.SupportsFileBasedCompression )
        print ("SystemCreationClassName: ", device.SystemCreationClassName , " SystemName: ", device.SystemName )
        print ("VolumeDirty: ", device.VolumeDirty , " VolumeName: ", device.VolumeName )
        print ("VolumeSerialNumber: ", device.VolumeSerialNumber )
        print ("")


def list_media_devices(devlist:list=None) ->list:
    """ alle removable-Laufwerke auflisten 
    Liste aus drive-Objekten
    """

    devices = []
    if not devlist:
        pythoncom.CoInitialize()
        c = wmi.WMI ()
        devlist = c.Win32_LogicalDisk () 
    for drive in devlist:
        # print (drive.Caption, DRIVE_TYPES[drive.DriveType])
        if drive.DriveType == 2:
            devices.append (drive.DeviceID)

    return devices



def get_device_name(device:str) ->str:
    """ Kompatibilität mit posix """
    return device

def get_media_path(device):
    return os.path.join (device, os.sep)

def mount(device, name=None):
    pass

def unmount(device, name=None):
    pass

def is_mounted(device):
    """ Kompatibilität mit posix:
    in win immer True
    """
    return os.path.ismount (device)


def is_removable(device:str, devlist:list=None):

    # devices = []
    if not devlist:
        c = wmi.WMI ()
        devlist = c.Win32_LogicalDisk () 
    for drive in devlist:
        if drive.DeviceID == device and drive.DriveType == 2:
            return True
    return False


def get_size(device:str, devlist:list=None):

    devices = []
    if not devlist:
        c = wmi.WMI ()
        devlist = c.Win32_LogicalDisk () 
    for drive in devlist:
        if drive.DeviceID == device:
            try:
                size = int (drive.Size)
            except:
                size = -1
            return size


def get_model(device:str, devlist:list=None):
    devices = []
    if not devlist:
        c = wmi.WMI ()
        devlist = c.Win32_LogicalDisk () 
    for drive in devlist:
        if drive.Caption == device:
            return drive.VolumeName
    return "unbekannt"


def get_vendor(device:str, devlist:list=None):
    """ in NT nicht verfügbar 
    Kompatibilität mit Posix
    """
    return "unbekannt"




def get_label(device:str, devlist:list=None) ->str:
    """ benutzerfreundlicher String zur Identifizierung von device
    """
    # devices = []
    if not devlist:
        c = wmi.WMI ()
        devlist = c.Win32_LogicalDisk () 
    for drive in devlist:
        if drive.Caption == device:
            if drive.VolumeName:
                name = drive.VolumeName
            else:
                name = "Unbenanntes Laufwerk"
            if drive.Size:
                size = "%.2f" % (int (drive.Size) /1024 ** 3) + " GB"
            else:
                size = "unbekannte Größe"
            
            if drive.FreeSpace:
                free = "%.2f" % ( int (drive.FreeSpace) /1024 ** 3) + " GB frei"
            else:
                free = "0 GB frei"
            return name  + ", " + size + " , " + free
    return "unbekannt"



if __name__ == "__main__":
    # alle Laufwerke:
    devicelist = list_drive_devices ()  
    # alle removable-Laufwerke
    medialist = list_media_devices (devicelist)    
    print ("Medialist:", medialist)      
    
    # for device in devicelist:
    # 	print("Drive:", get_device_name(device))
    # 	print("Mounted:", "Yes" if is_mounted(device) else "No")
    # 	print("Removable:", "Yes" if is_removable(device) else "No")
    # 	print("Size:", get_size(device), "bytes")
    # 	print("Size:", "%.2f" % (get_size(device) / 1024 ** 3), "GB")
    # 	print("Model:", get_model(device))
    # 	print("Vendor:", get_vendor(device))
    # 	print(" ")

    # drive_properties (medialist)
    for device in devicelist:
        name = device.Caption
        label = get_label (name, devicelist)
        print ("Label von {} {}".format (name, label))

