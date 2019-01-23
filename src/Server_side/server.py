#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

'''
Implementacion de factoria
'''
import sys
import pprint
import atexit

from work_queue import WorkQueue
from transfer_server import TransferI

import Ice # pylint: disable=E0401,C0411
import IceStorm # pylint: disable=E0401,C0411
Ice.loadSlice('downloader.ice')
import Downloader # pylint: disable=E0401,C0413

KEY = 'DownloaderApp.IceStorm/TopicManager'
TOPIC_NAME_SYNC = 'SyncTopic'
TOPIC_NAME_CLIENT = 'ProgressTopic'

class DownloaderSchedulerI(Downloader.DownloadScheduler, Downloader.SyncEvent):
    ''' Implementacion del Download Scheduler '''
    SongList = set()
    publisher_sync = None
    publisher_stats = None

    def __init__(self):
        ''' Constructor '''
        self.tasks = WorkQueue(self)
        self.tasks.start()

    def getSongList(self, current=None): # pylint: disable=C0103,W0613
        ''' Return a list and cast it '''
        return list(self.SongList)

    def addDownloadTask(self, url, current=None): #pylint: disable=C0103,W0613
        ''' Add a download task '''
        callback = Ice.Future()
        self.tasks.add(callback, url)
        return callback

    def get(self, song, current=None): #pylint: disable=C0103,W0613,R0201
        ''' Get a song from a server '''
        controller = TransferI(song)
        proxy = current.adapter.addWithUUID(controller)
        transfer = Downloader.TransferPrx.checkedCast(proxy)
        return transfer

    def requestSync(self, current=None): #pylint: disable=C0103,W0613
        ''' Request sync'''
        if self.publisher_sync is None:
            return
        self.publisher_sync.notify(list(self.SongList))

    def notify(self, songs, current=None): #pylint: disable=C0103,W0613
        ''' Notify '''
        songs = set(songs)
        self.SongList.union(songs)

class DownloaderFactoryI(Downloader.SchedulerFactory):
    '''Implementación de la factoria '''
    servants = {}
    qos = {}

    def __init__(self, sync_topic, progress_topic):
        self.sync_topic = sync_topic
        self.progress_topic = progress_topic

    def make(self, name, current=None):
        ''' Creación de una factoria '''
        if name in self.servants:
            raise Downloader.SchedulerAlreadyExists()
        servant = DownloaderSchedulerI()
        identity = Ice.stringToIdentity(name)
        proxy = current.adapter.add(servant, identity)
        proxy_sync = self.sync_topic.subscribeAndGetPublisher(self.qos, proxy)
        servant.publisher_sync = Downloader.SyncEventPrx.uncheckedCast(proxy_sync)
        proxy_stats = self.progress_topic.getPublisher()
        servant.publisher_stats = Downloader.ProgressEventPrx.uncheckedCast(proxy_stats)
        self.servants[name] = {'servant': servant, 'proxy': proxy, 'sync_proxy': proxy_sync}
        return Downloader.DownloadSchedulerPrx.checkedCast(proxy)

    def kill(self, name, current=None):
        ''' Destruir una factoria '''
        if name not in self.servants:
            raise Downloader.SchedulerNotFound()
        current.adapter.remove(Ice.stringToIdentity(name))
        self.sync_topic.unsubscribe(self.servants[name]['sync_proxy'])
        self.servants[name]['servant'].tasks.destroy()
        del self.servants[name]

    def availableSchedulers(self, current=None): #pylint: disable=C0103,W0613
        ''' Comprobar los schedulers disponibles'''
        pprint.pprint(self.servants, indent=4)
        return len(self.servants)


class Server(Ice.Application): #pylint: disable=R0903
    ''' Implementacion del Servidor '''
    servant = None

    def run(self, argv): #pylint: disable=W0613,W0221
        '''Run Server '''
        broker = self.communicator()
        topic_mgr_proxy = broker.stringToProxy(KEY)

        if topic_mgr_proxy is None:
            print("property {0} not set".format(KEY))
            return 1
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy) # pylint:disable=E1101

        if not topic_mgr:
            print(': invalid proxy')
            return 2

        try:
            topic_sync = topic_mgr.retrieve(TOPIC_NAME_SYNC)
        except IceStorm.NoSuchTopic: #pylint:disable=E1101
            topic_sync = topic_mgr.create(TOPIC_NAME_SYNC)

        try:
            topic_stats = topic_mgr.retrieve(TOPIC_NAME_CLIENT)
        except IceStorm.NoSuchTopic: #pylint:disable=E1101
            topic_stats = topic_mgr.create(TOPIC_NAME_CLIENT)

        self.servant = DownloaderFactoryI(sync_topic=topic_sync, progress_topic=topic_stats)
        adapter = broker.createObjectAdapter("DownloaderFactoryAdapter")
        proxy = adapter.addWithUUID(self.servant)
        print(proxy)
        sys.stdout.flush()
        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

    @atexit.register
    def shut_down(self):
        ''' Elimina a todos los sirvientes cuando se apague el server '''
        lista = self.servant.servants.keys()
        for name in lista:
            self.servant.kill(name)


SERVER = Server()
sys.exit(SERVER.main(sys.argv))
