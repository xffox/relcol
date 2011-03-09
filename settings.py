from model import Artist

import logging
import ConfigParser

class Settings:
    def __init__(self, path):
        self._artists = None
        self._interval = None
        self._command = None

        self._read(path)

    def __del__(self):
        pass

    def getArtists(self):
        if self._artists:
            return self._artists.copy()
        return None

    def getUpdateInterval(self):
        return self._interval

    def getCommand(self):
        return self._command

    def _read(self, path):
        self._setDefaults()

        config = ConfigParser.ConfigParser()
        if len(config.read([path])):
            for a in config.sections():
                if a != "global":
                    try:
                        name = config.get(a, "name")
                    except:
                        continue
                    try:
                        date = config.get(a, "date")
                    except:
                        date = None
                    try:
                        disambiguation = config.get(a, "disambiguation")
                    except:
                        disambiguation = None
                    self._artists.add(Artist(name, date, disambiguation))
                else:
                    try:
                        self._interval = config.getint(a, "interval")
                    except:
                        pass
                    try:
                        self._command = config.get(a, "command")
                    except:
                        pass
        else:
            logging.warning("settings read failed")

    def _setDefaults(self):
        if self._artists != None:
            self._artists.clear()
        else:
            self._artists = set()
        self._interval = 10
        self._command = None
