#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('../Server_side/downloader.ice')
# pylint: disable=E0401
import Downloader
import binascii
import uuid
import atexit
import cmd
import os.path
from cmd import Cmd

BLOCK_SIZE = 10240
CLIENT = None
KEY = 'DownloaderApp.IceStorm/TopicManager'
TOPIC_NAME = 'ProgressTopic'


@atexit.register
def shutdown(*args):
    if CLIENT is not None:
	    CLIENT.shutdown()

class ProgressEventI(Downloader.ProgressEvent):
    client = None
    def notify(self, clipData, current=None):
        if self.client is None:
            return 
        self.client.status[clipData.URL] = clipData.status
       
class Client(Ice.Application):
    status = {}
    qos = {}
    factory = None
    downloaderSch = None
    schedulerName = None
    proxy_progress = None
    progress_topic = None

    def run(self, argv):
        broker = self.communicator()
        proxy = broker.stringToProxy(argv[1])
        self.factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy)
        
        if not self.factory:
            raise RuntimeError('Invalid proxy')

        self.schedulerName = str(uuid.uuid4())
        self.downloaderSch = self.factory.make(self.schedulerName)

       
        topic_mgr_proxy = broker.propertyToProxy(KEY)

        if topic_mgr_proxy is None:
            print("property {0} not set".format(KEY))
            return 1
        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy)

        if not topic_mgr:
            print(': invalid proxy')
            return 2

        try:
            topic_progress = topic_mgr.retrieve(TOPIC_NAME)
        except IceStorm.NoSuchTopic:
            topic_progress = topic_mgr.create(TOPIC_NAME)

        self.progress_topic = topic_progress
        servant = ProgressEventI()
        servant.client = self
        self.proxy_progress = self.progress_topic.subscribeAndGetPublisher(self.qos, servant)   

    def addDownload(self, url):         
        # Async ami
        self.downloaderSch.addDownloadTaskAsync(url)

    def getFile(self, song, destination='./'):
        transfer = self.downloaderSch.get(song)
        self.receive(transfer, os.path.join(destination, song))

    def shutDown(self):
        self.factory.kill(self.schedulerName)
        self.progress_topic.unsubscribe(self.proxy_progress)
        self.progress_topic = None
        self.proxy_progress = None

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

class ShellClient(Cmd):
    def do_hello(self, args):
        """Esto es un ejemplo de lo que puede hacer la consola"""
        if len(args) == 0:
            name = 'stranger'
        else:
            name = args
        print("Hello, %s" % name)

    def do_quit(self, args):
        """Quits the program."""
        print("Quitting.")
        shutdown()
        raise SystemExit

def main():
    CLIENT = Client()
    prompt = ShellClient()
    prompt.prompt = '>'
    prompt.cmdloop('Iniciando ')
    sys.exit(CLIENT.main(sys.argv))
    
if __name__ == '__main__':
    main()


