import storage
from model import Artist, Release

import unittest
import os

class StorageTest(unittest.TestCase):
    _testFilename = "test.dat"

    def setUp(self):
        self._storage = storage.Storage()
        self._storage.connect(StorageTest._testFilename)

    def tearDown(self):
        self._storage.disconnect()
        os.remove(StorageTest._testFilename)

class ArtistAddTest(StorageTest):
    def testAddArtist(self):
        artist = Artist("Dropkick Murphy's")
        self._storage.addArtist(artist)

        self.assertTrue(artist in self._storage.getArtists())

class ReleaseAddTest(StorageTest):
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

class ArtistRemTest(StorageTest):
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

class ReleaseRemTest(StorageTest):
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

class NotFoundTest(StorageTest):
    def testArtistNotFound(self):
        with self.assertRaises(storage.KeyNotFound):
            self._storage.getArtist(0)

    def testReleaseNotFound(self):
        with self.assertRaises(storage.KeyNotFound):
            self._storage.getRelease(0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
