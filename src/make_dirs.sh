#!/bin/bash

rm -rf /tmp/youtube2mp3
rm -rf /tmp/db/registry
rm -rf /tmp/db/node1
echo "Limpieza ejecutada en /youtube2mp3, /registry y /node1"

mkdir -p /tmp/youtube2mp3
mkdir -p /tmp/db/registry
mkdir -p /tmp/db/node1
mkdir -p ./Songs
echo "Directorios necesarios creados"

echo "¿Desea usted eliminar las canciones del directorio /Songs? (y/n)"
read var1
if [ $var1 = y ]
then
	rm -rf ./Songs/*
	echo "Eliminadas todas las canciones"
fi

cd Server_side
echo "-----Lanzando nodo 1-----"
icegridnode --Ice.Config=node1.config

