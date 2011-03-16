from storage import StorageClient
from storage import KeyNotFound

# it's a really stupid way to use at

from datetime import datetime
import logging
import os

def _fromReleaseDate(releaseDate):
    if releaseDate == None:
        return None

    # use only day-precise format
    d = None
    try:
        d = datetime.strptime(releaseDate, "%Y-%m-%d")
    except ValueError:
        pass
    return d

class AtClient(StorageClient):
    def __init__(self, settings):
        StorageClient.__init__(self)

        self._settings = None

        if settings == None:
            raise ValueError
        self._settings = settings

    def storageChanged(self, storage):
        pass

    def artistAdded(self, artistKey):
        try:
            artist = self.getStorage().getArtist(artistKey)
        except KeyNotFound as e:
            logging.error( "key not found in storage: " + str(e.getKey()) )
            return

        logging.debug("artist added: " + str(artist))

    def artistRemoved(self, artistKey):
        logging.debug("artist removed")

    def releaseAdded(self, releaseKey):
        try:
            storage = self.getStorage()
            release = storage.getRelease(releaseKey)
            artist = storage.getArtist(release.getArtistKey())
            del storage
        except KeyNotFound as e:
            logging.error( "key not found in storage: " + str(e.getKey()) )
            return

        logging.debug("release added: " + str(artist) + str(release))

        d = _fromReleaseDate(release.getDate())
        if d == None:
            return

        logging.debug( "notification: %s '%s' '%s'" %
                (d.strftime("%x"), artist.getName(), release.getTitle()) )

        command = self._settings.getCommand()
        if command == None:
            return

        # use {artist}, {release} and {date} replacement fields in a command
        replacementFields = {"artist":artist.getName(), "release":release.getTitle(),
                "date":d.strftime("%x")}
        command = command.format(**replacementFields)
        logging.debug("execute: " + command) 
        os.system(command)

    def releaseRemoved(self, releaseKey):
        logging.debug("release removed")
