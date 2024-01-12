#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import os.path

import logging
import logging.config
from logging.handlers import RotatingFileHandler 

class Logbase ():
    """ class Loggingbase stellt die Basisdaten für die diversen logger 
    zur Verfügung.
    """
    def __init__(self) -> None:
        """ Defaultwerte festlegen, log-Dir anlegen 
        """
        # Log-Dateien liegen im Directory 'logs':
        thispath  = os.path.dirname(os.path.realpath(__file__))
        self.log_path = os.path.join (os.path.dirname (thispath), "logs")

        if not os.path.exists(self.log_path):
            os.makedirs (self.log_path)
        # else:
        #     print ("log-Dir bereits vorhanden.")

        # loglevel, siehe https://docs.python.org/3/howto/logging.html
        level = os.environ.get ("LOGLEVEL", default="WARNING")
        self.loglevel = getattr(logging, level.upper(), None)
        if not isinstance(self.loglevel, int):
            raise ValueError('Invalid log level: %s' % level)
        
        stream_formatter = logging.Formatter(
            '%(levelname)s: %(message)s [in %(filename)s:%(lineno)d]')
        stream_handler = logging.StreamHandler ()
        stream_handler.setFormatter (stream_formatter)
        stream_handler.setLevel (self.loglevel)

        logging.basicConfig (level=self.loglevel, handlers=[stream_handler])
        # logging.getLogger('').setLevel(logging.NOTSET)


    def logpath (self) -> str:
        """ liefert Pfad zu Log-Dir"""
        return self.log_path


    def filehandler (self, filename:str):
        """ liefert einen RotatingFileHandler

        filename: der Name des Logfiles
        """
        file_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(filename)s:%(lineno)d]')
        log_file = os.path.join (self.log_path, filename)
        file_handler = RotatingFileHandler(log_file, 
                        encoding= "utf-8", delay=True,
                        maxBytes=10240, backupCount=10)
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(self.loglevel)

        return file_handler


def readlogfile (fn:str, filterstr="") ->list:
    """ logfile lesen und als liste retournieren
    fn: Filename
    return: Liste der Zeilen
    """
    with open(fn, 'r', encoding="utf-8") as file:
        lines = [line.rstrip() for line in file]
    if filterstr:
        # filter loglines:
        filtered = []
        msgcont = False # log message continue on following lines
        for line in lines:
            date, msg = line.split (None, 1)
            try:
                year, month, day = date.split (sep='-') # no exception if begin log message
                msgcont = False
                if filterstr in line:
                    filtered.append (line)
                    msgcont = True
            except: # continued
                if msgcont:
                    filtered.append (line)
        return filtered
    
    return lines

# --- Main ----------------------------------------------------

if __name__ == "__main__":

    baselogger = Logbase ()
    logger = logging.getLogger ("foo")
    file_handler = baselogger.filehandler ("test.log")
    logger.addHandler (file_handler)

    logger.info ("Ich starte Main.")
    logger.warning ('Hello, warning message.')
