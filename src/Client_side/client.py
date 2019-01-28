#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

''' Implementación de un cliente desacoplado '''

import sys
import binascii
import uuid
import os.path
import re

from shell_client import Shell

import Ice #pylint:disable=E0401,C0411
import IceStorm #pylint:disable=E0401,C0411
Ice.loadSlice('../Server_side/downloader.ice')
import Downloader #pylint:disable=E0401,C0413


BLOCK_SIZE = 10240
CLIENT = None
KEY = 'DownloaderApp.IceStorm/TopicManager'
TOPIC_NAME = 'ProgressTopic'


class ProgressEventI(Downloader.ProgressEvent): # pylint: disable=R0903
    '''Implementacion de la interfaz Progress Event '''
    client = None
    def notify(self, clip_data, current=None): # pylint: disable=W0613
        ''' Notificar el estado de la URL '''
        if self.client is None:
            return
        self.client.status[clip_data.URL] = clip_data.status

class Client(Ice.Application):
    ''' Cliente típico de Ice '''
    status = {}
    qos = {}
    factory = None
    downloader_scheduler = None
    downloader_name = None
    progress_proxy = None
    progress_topic = None
    lista_canciones = []

    def run(self, argv): #pylint: disable=W0613,W0221
        ''' Arrancar el cliente '''
        broker = self.communicator()
        topic_mgr_proxy = broker.stringToProxy(KEY)

        if topic_mgr_proxy is None:
            print("Ha habido una problema al indicar el proxy {0}".format(KEY))
            return 1

        topic_mgr = IceStorm.TopicManagerPrx.checkedCast(topic_mgr_proxy) #pylint: disable=E1101

        if not topic_mgr:
            print('Proxy no válido')
            return 2
        try:
            progress_topic = topic_mgr.retrieve(TOPIC_NAME)
        except IceStorm.NoSuchTopic: #pylint: disable=E1101
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
        if self.progress_topic is None:
            return
        self.progress_topic.unsubscribe(self.progress_proxy)
        return 0

    def connect(self, endpoint):
        ''' Conectar y crear una factoria '''
        broker = self.communicator()
        proxy = broker.stringToProxy(endpoint)
        self.factory = Downloader.SchedulerFactoryPrx.checkedCast(proxy)

        if not self.factory:
            raise RuntimeError('Proxy no válido')

        self.downloader_name = str(uuid.uuid4())
        self.downloader_scheduler = self.factory.make(self.downloader_name)
        print("Factoria creada, scheduler->", self.downloader_name)

    def add_download(self, url):
        ''' Añadir descarga a la cola de trabajo de un scheduler '''
        if self.downloader_scheduler is None:
            raise RuntimeError('Conectese a una factoria')

        if yt_url_validation(url) is None:
            raise RuntimeError('Usted no ha introducido una url válida de youtube')
        self.downloader_scheduler.addDownloadTaskAsync(url)


    def get_songlist(self):
        ''' Obtener la lista de canciones '''
        if self.downloader_scheduler is None:
            raise RuntimeError('Conectese a una factoria')
        self.lista_canciones = self.downloader_scheduler.getSongList()
        return self.lista_canciones

    def available_schedulers(self):
        ''' Consultar los schedulers disponibles '''
        if self.downloader_scheduler is None:
            raise RuntimeError('Conectese a una factoria')
        print(self.factory.availableSchedulers())

    def get_file(self, song, destination='../Songs'):
        ''' Obtener un fichero del servidor al cliente '''
        if self.downloader_scheduler is None:
            raise RuntimeError('Conectese a una factoria')
        transfer = self.downloader_scheduler.get(song)
        receive(transfer, os.path.join(destination, song))

    def shut_down(self, name):
        ''' Desconectar todo '''
        if self.progress_proxy is None:
            return
        if self.progress_topic is None:
            return
        self.factory.kill(name)
        self.progress_topic.unsubscribe(self.progress_proxy)
        self.progress_topic = None
        self.progress_proxy = None

def receive(transfer, destination_file):
    ''' Transfer file over ICE implementation '''
    with open(destination_file, 'wb') as file_contents:
        remote_eof = False
        while not remote_eof:
            data = transfer.recv(BLOCK_SIZE)
            if len(data) > 1:
                data = data[1:]
            data = binascii.a2b_base64(data)
            remote_eof = len(data) < BLOCK_SIZE
            if data:
                file_contents.write(data)
        transfer.end()

def yt_url_validation(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    match = re.match(youtube_regex, url)

    if match:
        return match.group()


CLIENT = Client()
sys.exit(CLIENT.main(sys.argv))
