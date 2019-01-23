#!/bin/bash

sudo cp -p Server_side/downloader.ice /tmp/youtube2mp3
sudo cp -p Server_side/server.py /tmp/youtube2mp3
sudo cp -p Server_side/sync_timer.py /tmp/youtube2mp3
sudo cp -p Server_side/transfer_server.py /tmp/youtube2mp3
sudo cp -p Server_side/work_queue.py /tmp/youtube2mp3

icepatch2calc /tmp/youtube2mp3
echo "Ya es posible distribuir la aplicacion"
