#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('../Server_side/downloader.ice')
# pylint: disable=E0401
import Downloader
from cmd import Cmd


class Shell(Cmd):
    CLIENT = None
    prompt = ">>"
    
    def do_connect(self, argv):
        ''' Metodo que utilizaremos para conectarnos a la factoría
            Uso connect <Endpoint-factoria> ''' 
        try:
            self.CLIENT.connect(argv)
            self.prompt = "(on-line)>>"
        except Downloader.SchedulerAlreadyExists:
            print('Duplicated scheduler error reported')
        except Downloader.SchedulerNotFound:
            print('Non-existent scheduler error reported')
        except Exception as e:
            print("Error al introducir los argumentos " ,e)

    def do_checkStatus(self, argv):
        ''' Metodo que utilizaremos para comprobar el estado de las descargas '''
        print("Estado actual")
        try:
            print(self.CLIENT.status)
        except Exception as e:
            print("Error ",e)

    def do_addDownload(self, args):
        ''' Añade una cancion pasando como parámetro una url
            Uso addDownload <url_youtube> '''
        try:
            self.CLIENT.addDownload(args)
            print(type(args))
        except Exception as e:
            print("Ha habido un error", e)

    def do_getSongList(self, args):
        '''Obtiene la lista de canciones totales'''
        try: 
            lista_canciones = self.CLIENT.getSongList()
            print(lista_canciones)
        except Exception as e:
            print("Hubo un error", e)

    def do_get(self, args):
        ''' Metodo con el cual nos traemos a un <directorio> determinado una canción.
              Uso get <cancion> , el destino por defecto sera "./"
        '''
        try:
            self.CLIENT.getFile(args)
        except Exception as e:
            print("La cancion no existe o se ha equivocado en los argumentos", e)

    def do_availableSchedulers(self, args):
        '''Obtiene la cantidad de schedulers disponibles'''
        try:
            self.CLIENT.availableSchedulers()
        except Exception as e:
            print("No hay ningun scheduler creado", e)
            
    def do_kill(self, args):
        self.CLIENT.shutDown(args)

    def do_quit(self, args):
        '''Sale del programa'''
        print("-----Saliendo de youtube2mp3-------")
        return True

    def do_EOF(self, args):
        ''' Ctrl + D para salir de la shell youtube2mp3 '''
        return self.do_quit(args)
