#!/usr/bin/python3
# -*- mode:python; coding:utf-8; tab-width:4 -*-

'''
Transfer file over ICE implementation
'''


#################
#               #
#  CLIENT SIDE  #
#               #
#################

import binascii


BLOCK_SIZE = 10240


def receive(transfer, destination_file):
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

