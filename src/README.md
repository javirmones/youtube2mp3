## Dependencias
```
sudo pip install youtube-dl
```
## Trabajo pendiente
 1. Creación del canal de eventos y conexion de los DownloadSchedulers con el SyncTopic.
 2. Creación del cliente
   1. Solicitar la descarga de una URL correspondiente a un clip de Youtube.
   2. Recibir las notificaciones relativas al proceso de la descarga, y mostrarlo al usuario por algún medio, mediante la implementación de la interfaz *ProgressTopic*
   3. Obtención de los ficheros de audio.
   4. Obtención de la lista completa de ficheros descargados.
 3. Algunos arreglos más en el código
 4. Creación de la memoria de la práctica.
 
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
