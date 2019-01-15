#!/usr/bin/python3
# -*- mode:python; coding:utf-8; tab-width:4 -*-

'''
Simple task queue implementation
'''

from threading import Thread
from queue import Queue

import os.path
import youtube_dl
import Ice
# pylint: disable=C0413
Ice.loadSlice('downloader.ice')
# pylint: enable=C0413
# pylint: disable=E0401
import Downloader


class NullLogger:
    '''
    Logger used to disable youtube-dl output
    '''
    def debug(self, msg):
        '''Ignore debug messages'''

    def warning(self, msg):
        '''Ignore warnings'''

    def error(self, msg):
        '''Ignore errors'''


# Default configuration for youtube-dl
DOWNLOADER_OPTS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': NullLogger()
}


def _download_mp3_(url, destination='./'):
    '''
    Synchronous download from YouTube
    '''
    options = {}
    task_status = {}
    def progress_hook(status):
        task_status.update(status)
    options.update(DOWNLOADER_OPTS)
    options['progress_hooks'] = [progress_hook]
    options['outtmpl'] = os.path.join(destination, '%(title)s.%(ext)s')
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([url])
    filename = task_status['filename']
    # BUG: filename extension is wrong, it must be mp3
    filename = filename[:filename.rindex('.') + 1]
    return filename + options['postprocessors'][0]['preferredcodec']


class WorkQueue(Thread):
    '''Job Queue to dispatch tasks'''
    QUIT = 'QUIT'
    CANCEL = 'CANCEL'

    def __init__(self, scheduler):
        super(WorkQueue, self).__init__()
        self.scheduler = scheduler
        self.queue = Queue()

    def run(self):
        '''Task dispatcher loop'''
        for job in iter(self.queue.get, self.QUIT):
            job.download()
            self.queue.task_done()

        self.queue.task_done()
        self.queue.put(self.CANCEL)

        for job in iter(self.queue.get, self.CANCEL):
            job.cancel()
            self.queue.task_done()

        self.queue.task_done()

    def send_status(self, url, status):
        status_data = Downloader.ClipData()   
        status_data.URL = url     
        status_data.status = status     
        self.scheduler.publisher_stats.notify(status_data)
            

    def add(self, cb, url):
        '''Add new task to queue'''
        self.send_status(url, Downloader.Status.PENDING)
        self.queue.put(Job(cb, url, self))

    def destroy(self):
        '''Cancel tasks queue'''
        self.queue.put(self.QUIT)
        self.queue.join()


class Job:
    '''Task: clip to download'''
    def __init__(self, callback, url, work_queue):
        self.callback = callback
        self.url = url
        self.work_queue = work_queue

    def download(self):
        '''Donwload clip'''
        self.work_queue.send_status(self.url, Downloader.Status.INPROGRESS)
        result = _download_mp3_(self.url)
        self.work_queue.scheduler.SongList.add(result)
        self.work_queue.send_status(self.url, Downloader.Status.DONE)
        self.callback.set_result(result)


    def cancel(self):
        '''Cancel donwload'''
        self.work_queue.send_status(self.url, Downloader.Status.ERROR)
        self.callback.ice_exception(Downloader.SchedulerCancelJob())
