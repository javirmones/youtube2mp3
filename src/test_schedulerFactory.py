#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Usage: test_schedulerFactory "<factory endpoint>"
'''

import sys

import Ice
Ice.loadSlice('downloader.ice')
import Downloader


class FactoryTest(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy)

        if not factory:
            raise RuntimeError('Invalid factory proxy')

        print('Initial schedulers: %s' % factory.availableSchedulers())
        try:
            scheduler = factory.make('test')
        except Downloader.SchedulerAlreadyExists:
            print('Error: scheduler should not exists')
        print('Schedulers: %s' % factory.availableSchedulers())
        try:
            factory.make('test')
        except Downloader.SchedulerAlreadyExists:
            print('Duplicated scheduler error reported')
        factory.kill('test')
        print('Schedulers: %s' % factory.availableSchedulers())
        try:
            factory.kill('test')
        except Downloader.SchedulerNotFound:
            print('Non-existent scheduler error reported')
        
        return 0

sys.exit(FactoryTest().main(sys.argv))
