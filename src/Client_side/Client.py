#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('downloader.ice')
# pylint: disable=E0401
import Downloader
import binascii
import uuid
import atexit
import cmd


BLOCK_SIZE = 10240
CLIENT = None

@atexit.register
def shutdown(*args):
    if CLIENT is not None:
	    CLIENT.shutdown()

class Client(Ice.Application):
    factory=None
    downloaderSch = None
    schedulerName = None

    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        self.factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy)

        if not self.factory:
            raise RuntimeError('Invalid proxy')

        self.schedulerName = str(uuid.uuid4())
        self.downloaderSch = self.factory.make(self.schedulerName)

    def downloadUrl(self, url):
	    self.downloaderSch.addDownloadTask(url)

    def getList(self, song):
	    self.downloaderSch.get(song)

    def shutdown(self):
        self.factory.kill(self.schedulerName)

    '''
    Transfer file over ICE implementation
    '''
    def receive(self, transfer, destination_file):
            '''
            Read a complete file using a Downloader.Transfer object
            '''
            with open(destination_file, 'wb') as file_contents:
                remoteEOF = False
                while not remoteEOF:
                    data = transfer.recv(BLOCK_SIZE)
                    # Remove additional byte added by str() at server
                    if len(data) > 1:
                        data = data[1:]
                    data = binascii.a2b_base64(data)
                    remoteEOF = len(data) < BLOCK_SIZE
                    if data:
                        file_contents.write(data)
                transfer.end()

CLIENT = Client()
sys.exit(CLIENT.main(sys.argv))
