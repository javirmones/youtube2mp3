#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

'''
Implementacion de factoria
'''
import sys
import Ice
import IceStorm
Ice.loadSlice('downloader.ice')
# pylint: disable=E0401
import Downloader

from Work_queue import WorkQueue
from Transfer_server import TransferI

KEY = 'DownloaderApp.IceStorm/TopicManager'
TOPIC_NAME_SYNC = 'SyncTopic'
TOPIC_NAME_CLIENT = 'ProgressTopic'

class DownloaderSchedulerI(Downloader.DownloadScheduler, Downloader.SyncEvent):
    SongList = set()
    publisher_sync = None
    publisher_stats = None

    def __init__(self):
        self.tasks = WorkQueue(self)
        self.tasks.start()

    def getSongList(self, current=None):
        return list(self.SongList)

    def addDownloadTask(self, url, current=None):
        callback = Ice.Future()
        self.tasks.add(callback, url)
        return callback

    def get(self, song, current=None):
        controller = TransferI(song)
        proxy = current.adapter.addWithUUID(controller)
        transfer = Downloader.TransferPrx.checkedCast(proxy)
        return transfer

    def requestSync(self, current=None):
        if self.publisher_sync is None:
            return
        self.publisher_sync.notify(list(self.SongList))

    def notify(self, songs, current=None):
        songs = set(songs)
        self.SongList.union(songs)
        

class DownloaderFactoryI(Downloader.SchedulerFactory):
    servants = {}
   
    def __init__(self,syncTopic, progressTopic):
        self.syncTopic = syncTopic
        self.progressTopic = progressTopic

    def make(self, name, current=None):
        qos = {}
        if name in self.servants:
            raise Downloader.SchedulerAlreadyExists()
        servant = DownloaderSchedulerI()
        identity = Ice.stringToIdentity(name)
        proxy = current.adapter.add(servant, identity)
        proxy_sync = self.syncTopic.subscribeAndGetPublisher(qos, proxy)
        servant.publisher_sync = Downloader.SyncEventPrx.uncheckedCast(proxy_sync)
        proxy_stats = self.progressTopic.getPublisher()
        servant.publisher_stats = Downloader.ProgressEventPrx.uncheckedCast(proxy_stats)
        self.servants[name] = {'servant': servant, 'proxy': proxy, 'syncProxy': proxy_sync}
        return Downloader.DownloadSchedulerPrx.checkedCast(proxy)

    def kill(self, name, current=None):
        if name not in self.servants:
            raise Downloader.SchedulerNotFound()
        current.adapter.remove(Ice.stringToIdentity(name))
        self.syncTopic.unsubscribe(self.servants[name]['syncProxy'])
        self.servants[name]['servant'].tasks.destroy()
        del(self.servants[name])

    def availableSchedulers(self, current=None):
        return len(self.servants)


class Server(Ice.Application):
    def run(self, argv):
        
        broker = self.communicator()
        topic_mgr_proxy = broker.stringToProxy(KEY)

        if topic_mgr_proxy is None:
            print("property {0} not set".format(KEY))
            return 1
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy)

        if not topic_mgr:
            print(': invalid proxy')
            return 2

        try:
            topic_sync = topic_mgr.retrieve(TOPIC_NAME_SYNC)
        except IceStorm.NoSuchTopic:
            topic_sync = topic_mgr.create(TOPIC_NAME_SYNC)

        try:
            topic_stats = topic_mgr.retrieve(TOPIC_NAME_CLIENT)
        except IceStorm.NoSuchTopic:
            topic_stats = topic_mgr.create(TOPIC_NAME_CLIENT)

        servant = DownloaderFactoryI(syncTopic=topic_sync, progressTopic=topic_stats)
        adapter = broker.createObjectAdapter("DownloaderFactoryAdapter")
        proxy = adapter.addWithUUID(servant)

        print(proxy)
        sys.stdout.flush()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0

def main():
    server = Server()
    sys.exit(server.main(sys.argv))

if __name__ == '__main__':
    main()

