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
    progress_proxy = None
    progress_topic = None

    def run(self, endpoint):
        print(endpoint)
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
	shell = ShellClient()
	shell.CLIENT = self
	shell.cmdloop()
	#desuscribir el progress topic porque ya ha terminado cliente
        
        ################################################

    def connect(self, endpoint):
	proxy = broker.stringToProxy(endpoint)
        self.factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy)
        
        if not self.factory:
            raise RuntimeError('Invalid proxy')

        self.schedulerName = str(uuid.uuid4())
        self.downloaderSch = self.factory.make(self.schedulerName)
        print("Factoria creada con nombre",self.schedulerName)

    def addDownload(self, url):         
        # Async ami
        self.downloaderSch.addDownloadTaskAsync(url)
    
    def getSongList(self):
        listaCanciones = self.downloaderSch.getSongList()
        print(listaCanciones)

    def availableSchedulers(self):
        print(self.downloaderSch.availableSchedulers())

    def getFile(self, song, destination='./'):
        transfer = self.downloaderSch.get(song)
        self.receive(transfer, os.path.join(destination, song))

    def shutDown(self):
        self.factory.kill(self.schedulerName)
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

class ShellClient(Cmd):
    CLIENT = None
    

    def do_hello(self, args):
        '''Esto es un ejemplo de lo que puede hacer la consola'''
        if len(args) == 0:
            name = 'stranger'
        else:
            name = args
        print("Hello, %s" % name)
    
    def do_connect(self, args):
        ''' Metodo que utilizaremos para conectarnos a la factoría 
            Uso connect <Endpoint-factoria> '''
	
        try:
            #print(args)
            self.CLIENT.run(args)
	
        except Downloader.SchedulerAlreadyExists:
            print('Duplicated scheduler error reported')
        except Downloader.SchedulerNotFound:
            print('Non-existent scheduler error reported')
        

    def do_kill(self, args):
        '''Desconecta el cliente,el canal de comunicacion y mata la factoría'''
        shutdown()
    
    def do_addDownload(self, args):
        '''Añade una cancion con la url'''
        self.CLIENT.addDownload(args)
    
    def do_getSongList(self,args):
        '''Obtiene la lista de canciones'''
        self.CLIENT.getSongList()

    def do_availableSchedulers(self):
        '''Obtiene la cantidad de schedulers disponibles'''
        self.CLIENT.availableSchedulers()

    def do_quit(self, args):
        '''Sale del programa'''
        print("Quitting.")
        sys.exit(CLIENT.main(sys.argv))
        raise SystemExit

def main():
    prompt = ShellClient()
    prompt.prompt = '>'
    prompt.cmdloop('Iniciando youtube2mp3')
    #CLIENT = Client()
    

if __name__ == '__main__':
    main()


