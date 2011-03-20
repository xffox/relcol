import controller
import storage
import collector
import settings
import musicbrainz_source
from storage import InternalStorageError

import at_client

import logging
import os
import traceback

def run():
    try:
        _mkWorkDir()
    except:
        # nowhere to log anyway
        return

    logging.basicConfig(filename = _getWorkDir() + "/relcol.log",
            level = logging.DEBUG)

    try:
        _run()
    except Exception:
        logging.error(traceback.format_exc())

def _run():
    try:
        curSettings = settings.Settings(_getWorkDir() + "/conf.txt")
    except settings.ReadFailed:
        logging.warning("settings read failed")
        return

    curCollector = collector.Collector()
    curCollector.addSource(musicbrainz_source.MusicbrainzSource())

    curStorage = storage.Storage()
    try:
        with curStorage.connect(_getWorkDir() + "/save.dat"):
            curController = controller.Controller(curStorage, curCollector,
                    curSettings)

            atClient = at_client.AtClient(curSettings)
            atClient.setStorage(curStorage)

            curController.run()

    except InternalStorageError:
        logging.error("storage connect failed")
        raise

def _mkWorkDir():
    wd = _getWorkDir()
    if not os.path.exists(wd):
        os.mkdir(wd)

def _getWorkDir():
    return os.environ["HOME"] + "/.relcol/"
