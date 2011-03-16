from source import SourceError

class Collector:
    def __init__(self):
        self._sources = []

    def addSource(self, source):
        if source not in self._sources:
            self._sources.append(source)

    def remSource(self, source):
        self._sources.remove(source)

    def getArtists(self, name, date = None, disambiguation = None):
        artistResults = set()
        for source in self._sources:
            try:
                sourceArtistResults = source.getArtists(name, date, disambiguation)
            except SourceError:
                # reraise exception to break the cycle because without at least
                # one source the result is inconsistent
                raise

            for sar in sourceArtistResults:
                for ar in artistResults:
                    if ar == sar:
                        ar.merge(sar)
                        break
                else:
                    artistResults.add(sar)
        return artistResults

    def getReleases(self, artistResult):
        releaseResults = set()
        for source in self._sources:
            try:
                sourceReleaseResults = source.getReleases(artistResult)
            except SourceError:
                # reraise exception to break the cycle because without at least
                # one source the result is inconsistent
                raise

            for srr in sourceReleaseResults:
                for rr in releaseResults:
                    if rr == srr:
                        rr.merge(srr)
                        break
                else:
                    releaseResults.add(srr)
        return releaseResults
