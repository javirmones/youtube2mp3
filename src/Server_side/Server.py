#!/usr/bin/python3.6 -u
# -*- coding: utf-8 -*-
'''
Implementacion de factoria
'''

import sys
import Ice
import IceStorm
Ice.loadSlice('downloader.ice')
# pylint: disable=E0401
# error insalvable
import Downloader

from Work_queue import WorkQueue
from Transfer_server import TransferI

KEY = 'Downloader.IceStorm/TopicManager'
TOPIC_NAME = 'SyncTopic'

class DownloaderSchedulerI(Downloader.DownloadScheduler, Downloader.SyncEvent):
    SongList = set()
    publisher = None

    def getSongList(self, current=None):
        return list(self.SongList)

    def addDownloadTask(self, cb, url, current=None):
        #amd
        self.work_queue.add(cb, url)

    def get(self, song, current=None):
        return TransferI(song)

    def requestSync(self, current=None):
        if self.publisher is None:
            return
        self.publisher.notify(list(self.SongList))

    def notify(self, songs, current=None):
        songs=set(songs)
        self.SongList.union(songs)

        


class DownloaderFactoryI(Downloader.SchedulerFactory):
    servants = {}

    def __init__(self,syncTopic):
        self.topic=syncTopic

    def make(self, name, current=None):
        if name in self.servants:
            raise Downloader.SchedulerAlreadyExists()
        servant = DownloaderSchedulerI()
        qos = {}
        servant.publisher=self.topic.subscribeAndGetPublisher(qos, servant)
        identity = Ice.stringToIdentity(name)
        proxy = current.adapter.add(servant, identity)
        self.servants[name] = proxy
        return Downloader.DownloadSchedulerPrx.checkedCast(proxy)

    def kill(self, name, current=None):
        if name not in self.servants:
            raise Downloader.SchedulerNotFound()
        current.adapter.remove(Ice.stringToIdentity(name))
        del(self.servants[name])

    def availableSchedulers(self, current=None):
        return len(self.servants)


class Server(Ice.Application):
    def run(self, argv):
        # Esto ha quedado un poco en el aire, si cada DownloadScheduler va a tener una work_queue o si cada uno de ellos
        # la van a compartir
        work_queue = WorkQueue()
        broker = self.communicator()

        # Obtener el topic tal cual lo haciamos en la sesion 5
        topic_mgr_proxy = self.communicator().propertyToProxy(KEY)

        if topic_mgr_proxy is None:
            print("property {0} not set".format(KEY))
            return 1
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy)

        if not topic_mgr:
            print(': invalid proxy')
            return 2

        try:
            topic = topic_mgr.retrieve(TOPIC_NAME)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(TOPIC_NAME)

        # publisher = Downloader.SyncTopicPrx.uncheckedCast(topic.getPublisher())
        servant = DownloaderFactoryI(topic)
        adapter = broker.createObjectAdapter("DownloaderFactoryAdapter")
        proxy = adapter.addWithUUID(servant)

        print(proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))
