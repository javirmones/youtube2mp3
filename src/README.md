## Dependencias
**Youtube DL**
```
sudo pip install youtube-dl
```
Si no funcionase, intentar instalar la versión de la rama master de su repositorio github

```
git clone https://github.com/rg3/youtube-dl
cd youtube-dl
python3 setup.py install --user

```
**ZeroC Ice**
```
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv B6391CB2CFBA643D
sudo apt-add-repository "deb http://zeroc.com/download/Ice/3.7/ubuntu18.04 stable main"
sudo apt-get update
sudo apt-get install zeroc-ice-all-runtime zeroc-ice-all-dev

```
**Templates.xml**

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
1. **server.py**

*DownloaderFactoryI* es una interfaz del slice donde creamos, destruimos y comprobamos el número de factorias.
  * make -> Se crea una factoria con un scheduler y un uuid.
  * kill -> Destrucción de una factoría.
  * availableSchedulers -> Comprobar el número de schedulers disponibles.
  
*DownloadSchedulerI* es otra interfaz del slice, es un Downloader que tiene los siguientes métodos. 
 * addDonwloadTask -> Método para descargar los ficheros almacenados por el servidor en el cliente.
 * Transfer* get -> Almacenamiento de los archivos obtenidos tras el proceso de extracción del audio en un directorio local al servidor.
 * SongsList getSongsList -> Recepción de peticiones de listado de los audios como una secuencia de strings.
 
El *Server* es la clase principal que crea los canales de eventos y crea los schedulers.
El método *shut_down* -> Desconecta a todas las factorias al apagar el servidor.

2. **transfer_server.py** 

  * TransferI -> interfaz que se implementa del slice cuya misión es la transferencia de ficheros entre cliente y servidor..
  
3. **sync_timer.py **

*SyncTimer* 
  * *shot_events*

4. **work_queue.py**
Código de ayuda para implementar la cola de tareas en los servidores de descarga.
 * WorkQueue
 * Job

### Cliente
1. **client.py**

El cliente tiene las siguientes clases:

*ProgressEvent*
 *  notify
La clase client *Client*
 * connect
 * add_download
 * get_songlist
 * available_schedulers
 * get_file
 * shut_down
receive

2. **shell_client**

La clase Shell 
 * do_connect
 * do_check_status
 * do_add_download
 * do_get_songlist
 * do_get
 * complete_get
 * do_available_schedulers
 * do_kill
 * do_EOF
