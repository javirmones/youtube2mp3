#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' Implementación del Sync Timer '''

import time
import sys
import Ice # pylint: disable=E0401
import IceStorm # pylint: disable=E0401
Ice.loadSlice('downloader.ice')
import Downloader # pylint: disable=E0401,C0413

KEY = 'DownloaderApp.IceStorm/TopicManager'
TOPIC_NAME = 'SyncTopic'

class SyncTimer(Ice.Application): # pylint: disable=R0903
    '''Sync Timer class'''
    publisher = None

    def run(self, args): # pylint: disable=W0613
        '''Run Sync Timer'''
        broker = self.communicator()
        topic_mgr_proxy = broker.stringToProxy(KEY)

        if topic_mgr_proxy is None:
            print("Proxy invalido")
            return 1
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy) #pylint:disable=E1101

        if not topic_mgr:
            print("Error en el proxy")
            return 2
        try:
            topic = topic_mgr.retrieve(TOPIC_NAME)
        except IceStorm.NoSuchTopic: #pylint:disable=E1101
            topic = topic_mgr.create(TOPIC_NAME)

        self.publisher = Downloader.SyncEventPrx.uncheckedCast(topic.getPublisher())
        shot_events(self.publisher)
        return 0

def shot_events(publish):
    ''' Publish events in sync topic'''
    print("[sync_timer]: Start to publish")
    while True:
        publish.requestSync()
        time.sleep(5.0)

SYNC = SyncTimer()
EXIT = SYNC.main(sys.argv)
sys.exit(EXIT)
