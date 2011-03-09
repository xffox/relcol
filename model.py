class Artist:
    def __init__(self, name, date = None, disambiguation = None):
        self._name = name
        self._date = date
        self._disambiguation = disambiguation

    def getName(self):
        return self._name

    def getDate(self):
        return self._date

    def getDisambiguation(self):
        # regular expression to match artist's description
        return self._disambiguation

    def __eq__(self, other):
        try:
            return (self._name == other._name) and (
                    self._date == other._date) and (
                    self._disambiguation == other._disambiguation)
        except:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # different objects can have identical member strings concatenations
        # but it's ok for hash
        key = self._name
        if self._date:
            key += self._date
        if self._disambiguation:
            key += self._disambiguation
        return hash(key)

    def __str__(self):
        return str([self._name, self._date, self._disambiguation])

class Release:
    def __init__(self, title, date = None, tracksCount = None):
        self._title = title;
        self._date = date
        self._tracksCount = tracksCount
        
    def getTitle(self):
        return self._title

    def getDate(self):
        return self._date

    def getTracksCount(self):
        return self._tracksCount

    def __eq__(self, other):
        try:
            return (self._title == other._title) and (
                    self._date == other._date) and (
                    self._tracksCount == other._tracksCount)
        except:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # different objects can have identical member strings concatenations
        # but it's ok for hash
        key = self._title
        if self._date:
            key += self._date
        if self._tracksCount:
            key += str(self._tracksCount)
        return hash(key)

    def __str__(self):
        return str([self._title, self._date, self._tracksCount])
