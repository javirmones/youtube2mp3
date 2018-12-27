#!/usr/bin/python3.6 -u
# -*- coding: utf-8 -*-
'''
Implementacion de factoria
'''
import sys
import Ice
Ice.loadSlice('downloader.ice')
# pylint: disable=E0401
# error insalvable
import Downloader


class DownloaderSchedulerI(Downloader.DownloadScheduler):
    pass

class DownloaderFactoryI(Downloader.SchedulerFactory):
    servants = {}
    def make(self, name, current=None):
        if name in self.servants:
            raise Downloader.SchedulerAlreadyExists()
        servant = DownloaderSchedulerI()
        identity = Ice.stringToIdentity(name)
        proxy = current.adapter.add(servant, identity)
        print("Creados")
        self.servants[name] = proxy
        return Downloader.DownloadSchedulerPrx.checkedCast(proxy)

    def kill(self, name, current=None):
        if name not in self.servants:
            raise Downloader.SchedulerNotFound()
        current.adapter.remove(Ice.stringToIdentity(name))
        print("Destroy")
        del(self.servants[name])

    def availableSchedulers(self, current=None):
        return len(self.servants)



class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        servant = DownloaderFactoryI()

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
