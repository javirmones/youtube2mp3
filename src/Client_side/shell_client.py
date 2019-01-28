#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' Implementación de la shell del cliente'''

from cmd import Cmd
import Ice # pylint: disable=E0401
Ice.loadSlice('../Server_side/downloader.ice')
import Downloader # pylint: disable=E0401,C0413


class Shell(Cmd):
    ''' Clase shell '''
    CLIENT = None
    prompt = ">>"
    lista_canciones = []

    def do_connect(self, argv):
        '''
        Metodo que utilizaremos para conectarnos a la factoría
        Uso connect <Endpoint-factoria>
        '''
        try:
            self.CLIENT.connect(argv)
            self.prompt = "(on-line)>>"
        except Downloader.SchedulerAlreadyExists:
            print('Scheduler duplicado')
        except Downloader.SchedulerNotFound:
            print('Scheduler no encontrado')
        except Exception as err: # pylint:disable=W0703
            print("Error al introducir los argumentos ", err)

    def do_check_status(self, args): #pylint:disable=W0613
        ''' Metodo que utilizaremos para comprobar el estado de las descargas '''
        print("Estado actual")
        try:
            print(self.CLIENT.status)
        except Exception as err: # pylint:disable=W0703
            print("Error ", err)

    def do_add_download(self, args):
        ''' Añade una cancion pasando como parámetro una url
            Uso addDownload <url_youtube> '''
        try:
            self.CLIENT.add_download(args)
        except Exception as err: # pylint:disable=W0703
            print("Ha habido un error", err)

    def do_get_songlist(self, args): #pylint:disable=W0613
        '''Obtiene la lista de canciones totales'''
        try:
            song_list = self.CLIENT.get_songlist()
            for index in range(len(song_list)): #pylint:disable=C0200
                self.lista_canciones.append(song_list[index].replace('./', ''))
            print(self.lista_canciones)
        except Exception as err: # pylint:disable=W0703
            print("Hubo un error al obtener la lista", err)

    def do_get(self, args):
        ''' Metodo con el cual nos traemos a un <directorio> determinado una canción.
              Uso get <cancion> , el destino por defecto sera "./"
        '''
        try:
            self.CLIENT.get_file(args)
        except Exception as err: # pylint:disable=W0703
            print("La cancion no existe o se ha equivocado en los argumentos", err)

    def complete_get(self, text, line, start_index, end_index): #pylint:disable=W0613
        '''Autocompletar get '''
        if text:
            return [
                song for song in self.lista_canciones
                if song.startswith(text)
            ]
        return self.lista_canciones

    def do_available_schedulers(self, args): #pylint:disable=W0613
        '''Obtiene la cantidad de schedulers disponibles'''
        try:
            self.CLIENT.available_schedulers()
        except Exception as err: # pylint:disable=W0703
            print("No hay ningun scheduler creado", err)

    def do_quit(self, args): # pylint:disable=R0201,W0613
        '''Sale de la shell'''
        print("-----Saliendo de youtube2mp3-------")
        return True

    def do_kill(self, args):
        '''Aborta la conexión con una factoria Uso kill <nombre_sheduler>'''
        try:
            self.CLIENT.shut_down(args)
            self.prompt = ">>"
        except Downloader.SchedulerNotFound:
            print('Scheduler no encontrado')

    def do_EOF(self, args): # pylint:disable=C0103
        ''' Ctrl + D para salir de la shell youtube2mp3 '''
        return self.do_quit(args)
