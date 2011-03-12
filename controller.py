from source import SourceError
import controller

import logging
import time
import signal

class InvalidControllerInput(Exception):
    pass

class SignalException(Exception):
    pass

def _termHandler(signum, frame):
    logging.debug("SIGTERM")
    raise SignalException 

class Controller:
    def __init__(self, storage, source, settings):
        if storage == None:
            raise InvalidControllerInput("invalid storage")
        if source == None:
            raise InvalidControllerInput("invalid source")
        if settings == None:
            raise InvalidControllerInput("invalid settings")

        self._storage = storage 
        self._source = source
        self._settings = settings

    def setStorage(self, storage):
        self._storage = storage

    def setSettings(self, settings):
        self._settings = settings

    def run(self):
        termPrev = signal.signal(signal.SIGTERM, _termHandler)

        try:
            self._loop()
        except KeyboardInterrupt:
            logging.debug("keyboard interrupt")
        except SignalException:
            logging.debug("signal interrupt")
        finally:
            signal.signal(signal.SIGTERM, termPrev)

    def _loop(self):
        while True:
            self._update()
            interval = self._settings.getUpdateInterval()
            logging.debug("sleeping " + str(interval))
            time.sleep(interval)

    def _update(self):
        logging.debug("update")
        self._updateArtists(self._settings.getArtists())

    def _updateArtists(self, artists):
        artistResults = set()
        try:
            for a in artists:
                artistResults |= self._source.getArtists(a.getName(), a.getDate(),
                        a.getDisambiguation())
        except SourceError:
            logging.error("source error on the artists update")
            return
        logging.debug( "artist results count= " + str(len(artistResults)) )

        storageArtists = self._storage.getArtists()

        removedArtists = storageArtists - artistResults
        for ra in removedArtists:
            self._storage.remArtist(ra.getKey())
        del removedArtists

        addedArtists = artistResults - storageArtists
        for aa in addedArtists:
            self._storage.addArtist(aa)
        del addedArtists

        storageArtists = self._storage.getArtists()
        for sa in storageArtists:
            for ar in artistResults:
                if ar == sa:
                    self._updateReleases(sa, ar)
                    break
            else:
                pass

    def _updateReleases(self, artist, artistResult):
        if artist != artistResult:
            pass

        try:
            releaseResults = self._source.getReleases(artistResult)
        except SourceError:
            logging.error("source error on the releases update")
            return
        logging.debug( "release results count= " + str(len(releaseResults)) )

        storageReleases = self._storage.getReleases(artist.getKey())

        removeReleases = storageReleases - releaseResults
        for rr in removeReleases:
            self._storage.remRelease(rr.getKey())
        del removeReleases

        addedReleases = releaseResults - storageReleases
        for ar in addedReleases:
            self._storage.addRelease(artist.getKey(), ar)
        del addedReleases
