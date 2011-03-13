import storage
from model import Artist, Release

import unittest
import os

class StorageTestBase(unittest.TestCase):
    def setUp(self):
        self._storage = storage.Storage()

class NotConnectedStorageTest(StorageTestBase):
    def testDisconnect(self):
        with self.assertRaises(storage.InvalidStorageState):
            self._storage.disconnect()

    def testGetArtist(self):
        with self.assertRaises(storage.InvalidStorageState):
            self._storage.getArtist(0)

    def testGetRelease(self):
        with self.assertRaises(storage.InvalidStorageState):
            self._storage.getRelease(0)

    def testGetArtists(self):
        with self.assertRaises(storage.InvalidStorageState):
            self._storage.getArtists()

    def testGetReleases(self):
        with self.assertRaises(storage.InvalidStorageState):
            self._storage.getReleases(0)

    def testAddArtist(self):
        artist = Artist("Dropkick Murphy's")
        with self.assertRaises(storage.InvalidStorageState):
            self._storage.addArtist(artist)

    def testAddRelease(self):
        release = Release("Going Out in Style", "2011-03-01", 13)
        with self.assertRaises(storage.InvalidStorageState):
            self._storage.addRelease(0, release)

    def testRemArtist(self):
        with self.assertRaises(storage.InvalidStorageState):
            self._storage.remArtist(0)

    def testRemRelease(self):
        with self.assertRaises(storage.InvalidStorageState):
            self._storage.remRelease(0)

class ConnectedStorageTestBase(StorageTestBase):
    _testFilename = ":memory:"

    def setUp(self):
        StorageTestBase.setUp(self)
        self._storage.connect(ConnectedStorageTestBase._testFilename)

    def tearDown(self):
        self._storage.disconnect()
        if ConnectedStorageTestBase._testFilename != ":memory:":
            os.remove(ConnectedStorageTestBase._testFilename)

class InvalidArgumentTest(ConnectedStorageTestBase):
    def testGetArtist(self):
        with self.assertRaises(storage.InvalidArgument):
            self._storage.getArtist(None)

    def testGetRelease(self):
        with self.assertRaises(storage.InvalidArgument):
            self._storage.getRelease(None)

    def testGetReleases(self):
        with self.assertRaises(storage.InvalidArgument):
            self._storage.getReleases(None)

    def testAddArtist(self):
        with self.assertRaises(storage.InvalidArgument):
            self._storage.addArtist(None)

    def testAddRelease(self):
        release = Release("Going Out in Style", "2011-03-01", 13)
        with self.assertRaises(storage.InvalidArgument):
            self._storage.addRelease(None, release)

        with self.assertRaises(storage.InvalidArgument):
            self._storage.addRelease(0, None)

    def testRemArtist(self):
        with self.assertRaises(storage.InvalidArgument):
            self._storage.remArtist(None)

    def testRemRelease(self):
        with self.assertRaises(storage.InvalidArgument):
            self._storage.remRelease(None)

class ConnectedStorageTest(ConnectedStorageTestBase):
    def testRepeatedConnect(self):
        with self.assertRaises(storage.InvalidStorageState):
            self._storage.connect(ConnectedStorageTestBase._testFilename)

class ArtistAddTest(ConnectedStorageTestBase):
    def testAddArtist(self):
        artist = Artist("Dropkick Murphy's")
        self._storage.addArtist(artist)

        self.assertTrue(artist in self._storage.getArtists())

class ReleaseAddTest(ConnectedStorageTestBase):
    def testAddRelease(self):
        artist = Artist("Dropkick Murphy's")
        self._storage.addArtist(artist)

        for storageArtist in self._storage.getArtists():
            if storageArtist == artist:
                break
        else:
            assertTrue(False)

        release = Release("Going Out in Style", "2011-03-01", 13)
        self._storage.addRelease(storageArtist.getKey(), release)

        self.assertTrue( release in self._storage.getReleases(storageArtist.getKey()) )

class ArtistRemTest(ConnectedStorageTestBase):
    def testRemArtist(self):
        artist = Artist("Dropkick Murphy's")
        self._storage.addArtist(artist)

        for storageArtist in self._storage.getArtists():
            if storageArtist == artist:
                break
        else:
            self.assertTrue(False)

        self._storage.remArtist(storageArtist.getKey())

        self.assertFalse(artist in self._storage.getArtists())

class ReleaseRemTest(ConnectedStorageTestBase):
    def testRemRelease(self):
        artist = Artist("Dropkick Murphy's")
        self._storage.addArtist(artist)

        for storageArtist in self._storage.getArtists():
            if storageArtist == artist:
                break
        else:
            assertTrue(False)

        release = Release("Going Out in Style", "2011-03-01", 13)
        self._storage.addRelease(storageArtist.getKey(), release)

        for storageRelease in self._storage.getReleases(storageArtist.getKey()):
            if storageRelease == release:
                break
        else:
            self.assertTrue(False)

        self._storage.remRelease(storageRelease.getKey())

        self.assertFalse( release in self._storage.getReleases(storageArtist.getKey()) )

class NotFoundTest(ConnectedStorageTestBase):
    def testArtistNotFound(self):
        with self.assertRaises(storage.KeyNotFound):
            self._storage.getArtist(0)

    def testReleaseNotFound(self):
        with self.assertRaises(storage.KeyNotFound):
            self._storage.getRelease(0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
