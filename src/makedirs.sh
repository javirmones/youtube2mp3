#!/bin/bash

rm -rf IceStorm
rm -rf /tmp/youtube2mp3
rm -rf /tmp/db/{registry,node1}
echo "Limpieza ejecutada"
mkdir -p IceStorm
mkdir -p /tmp/youtube2mp3
mkdir -p /tmp/db/{registry,node1}
echo "Directorios creados"

icegridnode --Ice.Config=node1.config
