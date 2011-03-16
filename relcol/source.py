from model import Artist, Release

class SourceError(Exception):
    pass

class ArtistResult(Artist):
    def __init__(self, name, date = None, disambiguation = None):
        Artist.__init__(self, name, date, disambiguation)
        self._keys = {}

    def merge(self, artistResult):
        self._keys += artistResult._keys

    def getKey(self, source):
        return self._keys[source]

    def setKey(self, source, key):
        self._keys[source] = key

class ReleaseResult(Release):
    def __init__(self, title, date = None, tracksCount = None):
        Release.__init__(self, title, date, tracksCount)
        self._keys = {}

    def merge(self, releaseResult):
        self._keys += releaseResult._keys

    def getKey(self, source):
        return self._keys[source]

    def setKey(self, source, key):
        self._keys[source] = key

class Source:
    def __init__(self):
        pass

    def getArtists(self, name, date = None, disambiguation = None):
        return None

    def getReleases(self, artistResult):
        return None
