import sqlite3
import logging

from model import Artist, Release

# TODO: there is almost no error handling - fix it
# TODO: use keys instread of objects

class InvalidStorageState(Exception):
    pass

class InvalidArgument(Exception):
    pass

class InternalStorageError(Exception):
    pass

class KeyNotFound(Exception):
    def __init__(self, key):
        self._key = key

    def getKey(self):
        return self._key

class StorageClient:
    def __init__(self):
        self._storage = None

    def setStorage(self, storage):
        if self._storage == storage:
            return

        if self._storage != None:
            try:
                self._storage._remClient(self)
            except:
                logging.debug("removing client from disconnected storage")

        if storage != None:
            try:
                # references cycle - beware
                storage._addClient(self)
            except InvalidStorageState:
                raise
        self._storage = storage
        self.storageChanged(storage)

    def getStorage(self):
        return self._storage

    def storageChanged(self, storage):
        # override to add initial data reading
        pass

    def artistAdded(self, artistKey):
        pass

    def artistRemoved(self, artistKey):
        pass

    def releaseAdded(self, releaseKey):
        pass

    def releaseRemoved(self, releaseKey):
        pass

class StorageArtist(Artist):
    def __init__(self, key, name, date = None, disambiguation = None):
        Artist.__init__(self, name, date, disambiguation)
        self._key = key

    def getKey(self):
        return self._key

class StorageRelease(Release):
    def __init__(self, key, artistKey, title, date = None, tracksCount = None):
        Release.__init__(self, title, date, tracksCount)
        self._key = key
        self._artistKey = artistKey

    def getKey(self):
        return self._key

    def getArtistKey(self):
        return self._artistKey

class Storage:
    def __init__(self):
        self._clients = set()
        self._isConnected = False
        self._con = None

    def __del__(self):
        if self._isConnected:
            self.disconnect()

    def connect(self, path):
        if self._isConnected:
            raise InvalidStorageState("connecting to connected")

        self._con = sqlite3.connect(path)

        cur = self._con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS
                artist(
                name,
                date,
                disambiguation,
                PRIMARY KEY(name, date, disambiguation))""")
        cur.execute("""CREATE TABLE IF NOT EXISTS
                release(
                title,
                date,
                tracks_count INTEGER,
                artist_key INTEGER,
                PRIMARY KEY(title, date, tracks_count, artist_key),
                FOREIGN KEY(artist_key) REFERENCES artist(rowid)
                ON DELETE CASCADE ON UPDATE CASCADE)""")
        cur.close()

        self._isConnected = True
        logging.debug("storage connected")

    def disconnect(self):
        if not self._isConnected:
            raise InvalidStorageState("not connected")
        self._notifyClients(lambda c: c.setStorage(None))
        self._clients.clear()

        self._con.close()
        self._con = None

        self._isConnected = False
        logging.debug("storage disconnected")

    def getArtist(self, artistKey):
        if artistKey == None:
            raise InvalidArgument

        cur = self._con.cursor()
        cur.execute("""SELECT rowid, name, date, disambiguation FROM artist
                WHERE rowid=?""", (artistKey,))
        row = cur.fetchone()

        storageArtist = None
        if row != None:
            storageArtist = StorageArtist(row[0], row[1], row[2], row[3])

        cur.close()

        if storageArtist != None:
            return storageArtist
        raise KeyNotFound(artistKey)

    def getRelease(self, releaseKey):
        if releaseKey == None:
            raise InvalidArgument

        cur = self._con.cursor()
        cur.execute( """SELECT rowid, artist_key, title, date, tracks_count
                FROM release
                WHERE rowid=?""", (releaseKey,))
        row = cur.fetchone()

        storageRelease = None
        if row != None:
            storageRelease = StorageRelease(row[0], row[1], row[2], row[3], row[4])

        cur.close()

        if storageRelease != None:
            return storageRelease
        raise KeyNotFound(releaseKey)

    def getArtists(self):
        if not self._isConnected:
            raise InvalidStorageState("not connected")

        cur = self._con.cursor()
        cur.execute("SELECT rowid, name, date, disambiguation FROM artist")
        res = set()
        for r in cur:
            res.add(StorageArtist(r[0], r[1], r[2], r[3]))
        cur.close()
        return res

    def addArtist(self, artist):
        if not self._isConnected:
            raise InvalidStorageState("not connected")

        cur = self._con.cursor()
        cur.execute( """INSERT INTO artist(name, date, disambiguation)
                VALUES(?, ?, ?)""",
                (artist.getName(), artist.getDate(), artist.getDisambiguation()) )

        self._con.commit()

        ops = []
        if artist.getDate():
            ops.append("=")
        else:
            ops.append("is")
        if artist.getDisambiguation():
            ops.append("=")
        else:
            ops.append("is")
        cur.execute( """SELECT rowid FROM artist
                WHERE name=? AND date %s ?
                AND disambiguation %s ?""" % tuple(ops),
                (artist.getName(), artist.getDate(), artist.getDisambiguation()) )
        r = cur.fetchone()
        if r:
            artistKey = r[0]
        else:
            artistKey = None
        cur.close()

        if artistKey != None:
            self._notifyClients(lambda c: c.artistAdded(artistKey))
        else:
            raise InternalStorageError

    def remArtist(self, artistKey):
        if not self._isConnected:
            raise InvalidStorageState("not connected")

        # without foreign keys
        for release in self.getReleases(artistKey):
            self.remRelease(release.getKey())

        cur = self._con.cursor()
        cur.execute( "DELETE FROM artist WHERE rowid=?",
                (artistKey,) )
        cur.close()

        self._con.commit()

        self._notifyClients( lambda c: c.artistRemoved(artistKey) )

    def getReleases(self, artistKey):
        if not self._isConnected:
            raise InvalidStorageState("not connected")

        cur = self._con.cursor()
        cur.execute( """SELECT rowid, artist_key, title, date, tracks_count
                FROM release
                WHERE artist_key=?""",
                (artistKey,) )
        res = set()
        for r in cur:
            res.add(StorageRelease(r[0], r[1], r[2], r[3], r[4]))
        cur.close()
        return res

    def addRelease(self, artistKey, release):
        if not self._isConnected:
            raise InvalidStorageState("not connected")

        cur = self._con.cursor()
        cur.execute("""INSERT INTO release(title, date, tracks_count, artist_key)
                VALUES(?, ?, ?, ?)""",
                (release.getTitle(), release.getDate(), release.getTracksCount(),
                artistKey))

        self._con.commit()

        ops = []
        if release.getDate():
            ops.append("=")
        else:
            ops.append("is")
        if release.getTracksCount() != None:
            ops.append("=")
        else:
            ops.append("is")
        cur.execute("""SELECT rowid FROM release
                WHERE title=? AND date %s ?
                AND tracks_count %s ? AND artist_key=?""" % tuple(ops),
                (release.getTitle(), release.getDate(), release.getTracksCount(),
                artistKey))
        r = cur.fetchone()
        if r:
            releaseKey = r[0]
        else:
            releaseKey = None

        cur.close()

        if releaseKey != None:
            self._notifyClients(lambda c: c.releaseAdded(releaseKey))
        else:
            raise InternalStorageError

    def remRelease(self, releaseKey):
        if not self._isConnected:
            raise InvalidStorageState("not connected")

        cur = self._con.cursor()
        cur.execute( "DELETE FROM release WHERE rowid=?",
                (releaseKey,) )
        cur.close()

        self._con.commit()

        self._notifyClients(lambda c: c.releaseRemoved(releaseKey))

    def _addClient(self, storageClient):
        if not self._isConnected:
            raise InvalidStorageState("not connected")
        self._clients.add(storageClient)

    def _remClient(self, storageClient):
        if not self._isConnected:
            raise InvalidStorageState("not connected")
        self._clients.remove(storageClient)

    def _notifyClients(self, notify):
        # notify is lambda with notification
        # use copy because notify can alter the clients list
        clients = self._clients.copy();
        for c in clients:
            notify(c)
