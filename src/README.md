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

Una vez hecho, active todos los servicios pulsando sobre ellos el botón enable.

Después ejecutamos el cliente:

```
./client.py --Ice.Config=client.config
```
### Servidor
1. **server.py**

La clase *DownloaderFactoryI* es una interfaz del slice donde creamos, destruimos y comprobamos el número de factorias.
  * make -> se crea una factoria con un scheduler y un uuid.
  * kill -> destrucción de una factoría.
  * availableSchedulers -> comprobar el número de schedulers disponibles.
  
La clase *DownloadSchedulerI* es otra interfaz del slice, es un Downloader que tiene los siguientes métodos. 
 * addDonwloadTask -> método para descargar los ficheros almacenados por el servidor en el cliente.
 * Transfer* get -> almacenamiento de los archivos obtenidos tras el proceso de extracción del audio en un directorio local al servidor.
 * SongsList getSongsList -> recepción de peticiones de listado de los audios como una secuencia de strings.
 
El *Server* es la clase principal que crea los canales de eventos y crea los schedulers.
El método *shut_down* -> desconecta a todas las factorias al apagar el servidor, utiliza el decorador @atexit para poder salir.

2. **transfer_server.py** 

  * TransferI -> interfaz que se implementa del slice cuya misión es la transferencia de ficheros entre cliente y servidor..
  
3. **sync_timer.py**

  * *shot_events* -> dispara los eventos de sincronización en el canal de eventos SyncTopic.

4. **work_queue.py** -> código de ayuda para implementar la cola de tareas en los servidores de descarga.

### Cliente
1. **client.py**

El cliente tiene las siguientes clases:

La clase *ProgressEventI* es la implementación de la interfaz en la cual se trata de notificar de los cambios de estado en una canción mediante el uso del método *notify* en el canal de eventos ProgressTopic.
 
La clase *Client* se divide en dos partes, al tratar de realizar el desarrollo se ha realizado un cliente pesado y una shell que utilizará dicho cliente, tiene los siguientes métodos.
 * connect -> conexión del cliente al servidor haciendo uso del método *make*.
 * add_download -> añadir a la work_queue una descarga con una url.
 * get_songlist -> obtener la lista de canciones pertinente al scheduler.
 * available_schedulers -> comprueba la cantidad de schedulers disponibles para un determinado cliente.
 * get_file -> transferencia de fichero desde el servidor al cliente.
 * shut_down -> desconexión de un scheduler y eliminación de los canales de eventos.
receive -> el método receive es un método auxiliar que consta de la transferencia entre archivos entre cliente y servidor.

2. **shell_client**

La clase *Shell* es la parte ligera que compone al cliente simplemente los métodos de esta clase utilizarán los métodos del cliente, salvo el método *complete_get* que se utilizará para hacer que sea mas sencilla la obtención de una canción desde el servidor sin que sea necesario poner el nombre completo de la canción que se quiera obtener, basta con pulsar TAB para autocompletar.

Usando el comando *help* <nombre_metodo> tendremos ayuda disponible para el uso de cada método en la shell.

