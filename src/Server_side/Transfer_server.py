import binascii

import sys
import Ice
Ice.loadSlice('downloader.ice')
# pylint: disable=E0401
import Downloader

class TransferI(Downloader.Transfer):
    '''
    Transfer file
    '''
    def __init__(self, local_filename):
        self.file_contents = open(local_filename, 'rb')

    def recv(self, size, current=None):
        '''Send data block to client'''
        return str(
            binascii.b2a_base64(self.file_contents.read(size), newline=False)
        )

    def end(self, current=None):
        '''Close transfer and free objects'''
        self.file_contents.close()
        current.adapter.remove(current.id)
