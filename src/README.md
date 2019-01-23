## Dependencias
Youtube DL: (Si no funcionara instalar desde su repositorio en github)
```
sudo pip install youtube-dl
```
ICE
```
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv B6391CB2CFBA643D
sudo apt-add-repository "deb http://zeroc.com/download/Ice/3.7/ubuntu18.04 stable main"
sudo apt-get update
sudo apt-get install zeroc-ice-all-runtime zeroc-ice-all-dev

```
Templates.xml

Debido a que se utilizará el servicio IcePatch2, se usará por lo tanto una versión de la plantilla más vieja:
```
sudo pip install youtube-dl
```


## Estructura de archivos
Crea todos los directorios necesarios (limpiandolos previamente) para el inicio de la práctica y ejecuta el nodo principal.
1.  makedirs.sh

Copia los archivos necesarios que necesiten ser distribuidos y los binariza con icepatch2calc.

2. startPathDistribution.sh

Ambos archivos se ejecutan de la siguiente manera:
```
chmod +x <nombre_archivo>.sh
./<nombre_archivo>.sh
```
### Lado del Servidor
1. Server.py

*DownloaderFactoryI* es un método del slice donde creamos, destruimos y comprobamos el número de  factorias.

No obstante se ha utilizado el archivo *testSchedulerFactory.py* para probar la factoría.
El orden de ejecución es el siguiente:

  1. ./makedirs.sh -> Esto nos ejecutará el nodo 1 el cual imprimirá por consola el Endpoint de la factoria.
  2. ./startPathDistribution.sh 
  3. icegridgui -> Crear conexion y cargar el archivo downloader.xml -> Save to a registry -> Apply path distribution
  4. ./testSchedulerFactory.py --Ice.Config=locator.config "Endpoint factoria"

*DownloadSchedulerI* es otro método del slice, el cual es un Downloader sus métodos son los siguientes:
 * addDonwloadTask(string url); -> Almacenamiento de los archivos obtenidos tras el proceso de extracción del audio en un directorio local al servidor.
 * Transfer* get(string song); -> Método para descargar los ficheros almacenados por el servidor en el cliente.
 * SongsList getSongsList(); -> Recepción de peticiones de listado de los audios como una secuencia de strings.

*Creación del canal de eventos*
TO - DO
 
2. Transfer_server.py
3. SyncTimer.py

### Lado del cliente
1. Client.py

TO - DO
