#!/bin/bash
 
mkdir -p IceStorm
mkdir -p /tmp/youtube2mp3
mkdir -p /tmp/db/{registry,node1}
echo "Directorios creados"

icegridnode --Ice.Config=node1.config
