#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Transferencia de archivos entre cliente y servidor
'''
import binascii
import Ice # pylint:disable=E0401
Ice.loadSlice('downloader.ice')
import Downloader # pylint:disable=E0401,C0413

class TransferI(Downloader.Transfer):
    '''
    Transferir archivo
    '''
    def __init__(self, local_filename):
        self.file_contents = open(local_filename, 'rb')

    def recv(self, size, current=None): #pylint:disable=W0105,W0613
        '''Send data block to client'''
        return str(
            binascii.b2a_base64(self.file_contents.read(size), newline=False)
        )

    def end(self, current=None):
        '''Close transfer and free objects'''
        self.file_contents.close()
        current.adapter.remove(current.id)
