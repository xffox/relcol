from source import ArtistResult, ReleaseResult, SourceError

import re
from musicbrainz2.webservice import Query, WebServiceError
from musicbrainz2.webservice import ArtistFilter, ReleaseFilter

class MusicbrainzSource:
    _sourceName = "musicbrainz"

    def getArtists(self, name, date = None, disambiguation = None):
        q = Query()

        if disambiguation:
            disPattern = re.compile(disambiguation, re.I)
        else:
            disPattern = None

        offset = 0
        limit = 100
        artistResults = set()
        while True:
            try:
                f = ArtistFilter(name = name, offset = offset, limit = limit)
                results = q.getArtists(f)
            except WebServiceError, e:
                raise SourceError

            results = filter(lambda res: res.getScore() == 100, results)
            # use filtered count because resulsts are score-ordered
            count = len(results)

            results = filter(lambda res: 
                    (not date or res.getArtist().getBeginDate() == date)
                    and ( not disPattern or
                        disPattern.search(res.getArtist().getDisambiguation()) ),
                    results)

            for r in results:
                ar = ArtistResult(name = r.getArtist().getName(),
                        date = r.getArtist().getBeginDate(),
                        disambiguation = disambiguation)
                        # use original disambiguation cause it'll be used in 
                        # artist's comparation

                ar.setKey(MusicbrainzSource._sourceName, r.getArtist().getId())
                artistResults.add(ar)

            if count < limit:
                break
            offset += count
        return artistResults

    def getReleases(self, artistResult):
        q = Query()

        offset = 0
        limit = 100
        releaseResults = set()
        while True:
            try:
                f = ReleaseFilter(artistId = 
                        artistResult.getKey(MusicbrainzSource._sourceName),
                        offset = offset, limit = limit)
                results = q.getReleases(f)
            except WebServiceError, e:
                raise SourceError

            count = len(results)

            results = filter(lambda res: res.getScore() == 100, results)

            for r in results:
                rr = ReleaseResult(title = r.getRelease().getTitle(),
                        date = r.getRelease().getEarliestReleaseDate(),
                        tracksCount = r.getRelease().getTracksCount())
                rr.setKey(MusicbrainzSource._sourceName, r.getRelease().getId())
                releaseResults.add(rr)

            if count < limit:
                break
            offset += count
        return releaseResults 
