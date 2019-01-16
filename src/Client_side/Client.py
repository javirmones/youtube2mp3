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
from ShellClient import Shell

BLOCK_SIZE = 10240
CLIENT = None
KEY = 'DownloaderApp.IceStorm/TopicManager'
TOPIC_NAME = 'ProgressTopic'

@atexit.register
def shutdown(*args):
    if CLIENT is not None:
	    CLIENT.shutDown()

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
    progress_proxy = None
    progress_topic = None
    lista_canciones = []

    def run(self, argv):
        try:   
            broker = self.communicator()
            topic_mgr_proxy = broker.stringToProxy(KEY)

            if topic_mgr_proxy is None:
                print("Ha habido una problema al indicar el proxy {0}".format(KEY))
                return 1

            topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy)
        
            if not topic_mgr:
                print('Proxy no válido')
                return 2

            try:
                progress_topic = topic_mgr.retrieve(TOPIC_NAME)
            except IceStorm.NoSuchTopic:
                progress_topic = topic_mgr.create(TOPIC_NAME)

            self.progress_topic = progress_topic
            servant = ProgressEventI()
            adapter = broker.createObjectAdapter("DownloaderFactoryAdapter")
            servant.client = self
            proxy = adapter.addWithUUID(servant)
            self.progress_proxy = self.progress_topic.subscribeAndGetPublisher(self.qos, proxy)
            adapter.activate()   
            self.shutdownOnInterrupt()
            shell = Shell()
            shell.CLIENT = self
            shell.cmdloop('-----Iniciando youtube2mp3-----')
            self.progress_topic.unsubscribe(self.progress_proxy)

        except Exception:
            print("Tio el archivo de configuración")

    def connect(self, endpoint):
        broker = self.communicator()
        proxy = broker.stringToProxy(endpoint)
        self.factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy)
        
        if not self.factory:
            raise RuntimeError('Proxy no válido')

        self.schedulerName = str(uuid.uuid4())
        self.downloaderSch = self.factory.make(self.schedulerName)
        print("Factoria creada, scheduler->", self.schedulerName)

    def addDownload(self, url):         
        if self.downloaderSch is None:
            raise RuntimeError('Conectese a una factoria')
        self.downloaderSch.addDownloadTaskAsync(url)
    
    def getSongList(self):
        if self.downloaderSch is None:
            raise RuntimeError('Conectese a una factoria')
        self.lista_canciones = self.downloaderSch.getSongList()
        return self.lista_canciones

    def availableSchedulers(self):
        if self.downloaderSch is None:
            raise RuntimeError('Conectese a una factoria')
        print(self.factory.availableSchedulers())

    def getFile(self, song, destination='../Songs'):
        if self.downloaderSch is None:
            raise RuntimeError('Conectese a una factoria')
        transfer = self.downloaderSch.get(song)
        self.receive(transfer, os.path.join(destination, song))

    def shutDown(self, name):
        # Esto hay que mejorarlo           
        self.factory.kill(name)
        self.progress_topic.unsubscribe(self.progress_proxy)
        self.progress_topic = None
        self.progress_proxy = None

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


