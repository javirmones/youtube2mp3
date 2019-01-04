#!/bin/bash

rm -rf /tmp/youtube2mp3
rm -rf /tmp/db/{registry,node1}
echo "Limpieza ejecutada"

mkdir -p /tmp/youtube2mp3
mkdir -p /tmp/db/{registry,node1}
echo "Directorios creados"

cd Server_side
echo "-----Lanzando nodo 1-----"
icegridnode --Ice.Config=node1.config

