#!/bin/bash

sudo cp -p Server_side/downloader.ice /tmp/youtube2mp3
sudo cp -p Server_side/Server.py /tmp/youtube2mp3

icepatch2calc /tmp/youtube2mp3
echo "Ya es posible distribuir la aplicacion"
