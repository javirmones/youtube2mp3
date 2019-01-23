## Dependencias
Youtube DL: (Si no funcionara instalar desde su repositorio en github)
```
sudo pip install youtube-dl
```
ZeroC Ice
```
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv B6391CB2CFBA643D
sudo apt-add-repository "deb http://zeroc.com/download/Ice/3.7/ubuntu18.04 stable main"
sudo apt-get update
sudo apt-get install zeroc-ice-all-runtime zeroc-ice-all-dev

```
Templates.xml

Debido a que se utilizará el servicio IcePatch2, se usará por lo tanto una versión de la plantilla más vieja, que usted deberá copiar en el directorio /usr/share/ice. [Templates.xml](https://github.com/javirmones/youtube2mp3/blob/development/resources/templates.xml)


## Ejecución del proyecto

Crea todos los directorios necesarios (limpiandolos previamente) para el inicio de la práctica y ejecuta el nodo principal.
1.  make_dirs.sh

Copia los archivos necesarios que necesiten ser distribuidos y los binariza con icepatch2calc.

2. start_distrib.sh

Ambos archivos se ejecutan de la siguiente manera: (si hubiera algun problema con los permisos, se usaría chmod)
```
chmod +x <nombre_archivo>.sh
./<nombre_archivo>.sh
```
Una vez ejecutados sendos comandos, procederemos a abrir la interfaz gráfica de Ice:
```
icegridgui
```
Se crea una nueva conexión con el nodo que se esta ejecutando, se abre el archivo *downloader.xml* con Open -> Open From File, y se tendrá el proyecto *DownloaderApp*, que deberemos guardar en el registro con -> Save to a Registry.

Una vez realizado este proces se cambiará a la pestaña Live Deployment, comprobará que efectivamente puede aplicar la distribución de la aplicación, y realizará Tools -> Application -> Apply path distribution.

Una vez hecho active todos los servicios pulsando sobre ellos el botón enable.

### Servidor
1. server.py

*DownloaderFactoryI* es un método del slice donde creamos, destruimos y comprobamos el número de factorias.
  * make
  * kill
  * availableSchedulers

*DownloadSchedulerI* es otro método del slice, es un Downloader que tiene los siguientes métodos. 
 * addDonwloadTask(string url); -> Método para descargar los ficheros almacenados por el servidor en el cliente.
 * Transfer* get(string song); -> Almacenamiento de los archivos obtenidos tras el proceso de extracción del audio en un directorio local al servidor.
 * SongsList getSongsList(); -> Recepción de peticiones de listado de los audios como una secuencia de strings.
  
*Canales de eventos*
  * Sync Topic
  * Progress Topic
 
2. transfer_server.py
  * asdf

3. sync_timer.py
  * er

4. work_queue.py

### Cliente
1. client.py
*ProgressEvent*


2. shell_client
asd

