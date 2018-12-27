## Dependencias
```
sudo pip install youtube-dl
```

## Estructura de archivos
1.  makedirs.sh

Crea todos los directorios necesarios (limpiandolos previamente) para el inicio de la práctica y ejecuta el nodo principal.

2. startPathDistribution.sh

Copia los archivos necesarios que necesiten ser distribuidos y los binariza con icepatch2calc.

Ambos archivos se ejecuta de la siguiente manera:
```
chmod +x <nombre_archivo>.sh
./<nombre_archivo>.sh
```
3. Server.py

Se ha procedido a la implementación de *DownloaderFactoryI* con el cual creamos las factorias, las destruimos y comprobamos la cantidad que hay.

No obstante se ha utilizado el archivo *testSchedulerFactory.py* para probar la factoría.
El orden de ejecución es el siguiente:
  * ./makedirs.sh -> Esto nos ejecutará el nodo 1 el cual imprimirá por consola el Endpoint de la factoria
  * ./startPathDistribution.sh 
  * icegridgui -> y cargar el archivo downloader.xml -> save to a registry -> apply path distribution
  * ./testSchedulerFactory.py --Ice.Config=locator.config "Endpoint factoria"
  
